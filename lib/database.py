from __future__ import annotations

import json
import sqlite3
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from lib.utils import compress_image, generate_quiz_code

ROOT = Path(__file__).resolve().parent.parent
LOCAL_DB = ROOT / "data" / "local.db"
PHOTO_DIR = ROOT / "data" / "photos"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database(ABC):
    @abstractmethod
    def create_quiz(self, title: str) -> dict[str, Any]: ...

    @abstractmethod
    def get_quiz(self, quiz_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def get_quiz_by_code(self, code: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def list_quizzes(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def set_quiz_deployed(self, quiz_id: str, deployed: bool) -> None: ...

    @abstractmethod
    def delete_quiz(self, quiz_id: str) -> None: ...

    @abstractmethod
    def add_question(
        self,
        quiz_id: str,
        question_text: str,
        options: list[str],
        correct_index: int,
    ) -> dict[str, Any]: ...

    @abstractmethod
    def list_questions(self, quiz_id: str, *, active_only: bool = False) -> list[dict[str, Any]]: ...

    @abstractmethod
    def set_question_enabled(self, question_id: str, enabled: bool) -> None: ...

    @abstractmethod
    def delete_question(self, question_id: str) -> None: ...

    @abstractmethod
    def import_quiz_json(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def submit_quiz(
        self,
        quiz_id: str,
        student_name: str,
        answers: dict[str, int],
    ) -> dict[str, Any]: ...

    @abstractmethod
    def list_submissions(self, quiz_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def add_student(self, name: str, photo_bytes: bytes) -> dict[str, Any]: ...

    @abstractmethod
    def list_students(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_photo_bytes(self, photo_path: str) -> bytes | None: ...

    @property
    @abstractmethod
    def backend_name(self) -> str: ...


class LocalDatabase(Database):
    def __init__(self) -> None:
        LOCAL_DB.parent.mkdir(parents=True, exist_ok=True)
        PHOTO_DIR.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(LOCAL_DB, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                create table if not exists quizzes (
                    id text primary key,
                    title text not null,
                    code text not null unique,
                    deployed integer not null default 0,
                    created_at text not null
                );
                create table if not exists questions (
                    id text primary key,
                    quiz_id text not null,
                    sort_order integer not null default 0,
                    question_text text not null,
                    options text not null,
                    correct_index integer not null,
                    enabled integer not null default 1,
                    foreign key (quiz_id) references quizzes(id) on delete cascade
                );
                create table if not exists submissions (
                    id text primary key,
                    quiz_id text not null,
                    student_name text not null,
                    score integer not null,
                    total integer not null,
                    submitted_at text not null,
                    foreign key (quiz_id) references quizzes(id) on delete cascade
                );
                create table if not exists submission_answers (
                    id text primary key,
                    submission_id text not null,
                    question_id text not null,
                    selected_index integer not null,
                    is_correct integer not null,
                    foreign key (submission_id) references submissions(id) on delete cascade
                );
                create table if not exists students (
                    id text primary key,
                    name text not null,
                    photo_path text not null,
                    created_at text not null
                );
                """
            )
            try:
                conn.execute(
                    "alter table questions add column enabled integer not null default 1"
                )
            except sqlite3.OperationalError:
                pass

    def _normalize_question(self, q: dict[str, Any]) -> dict[str, Any]:
        q["options"] = json.loads(q["options"]) if isinstance(q["options"], str) else q["options"]
        q["enabled"] = bool(q.get("enabled", 1))
        return q

    @property
    def backend_name(self) -> str:
        return "local (SQLite)"

    def create_quiz(self, title: str) -> dict[str, Any]:
        quiz_id = str(uuid.uuid4())
        code = generate_quiz_code()
        with self._connect() as conn:
            while conn.execute("select 1 from quizzes where code = ?", (code,)).fetchone():
                code = generate_quiz_code()
            conn.execute(
                "insert into quizzes (id, title, code, deployed, created_at) values (?, ?, ?, 0, ?)",
                (quiz_id, title, code, _now_iso()),
            )
        return self.get_quiz(quiz_id)  # type: ignore[return-value]

    def get_quiz(self, quiz_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("select * from quizzes where id = ?", (quiz_id,)).fetchone()
        return dict(row) if row else None

    def get_quiz_by_code(self, code: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "select * from quizzes where code = ? and deployed = 1",
                (code.strip().upper(),),
            ).fetchone()
        if row:
            quiz = dict(row)
            quiz["deployed"] = bool(quiz["deployed"])
            return quiz
        return None

    def list_quizzes(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select * from quizzes order by created_at desc").fetchall()
        result = []
        for row in rows:
            quiz = dict(row)
            quiz["deployed"] = bool(quiz["deployed"])
            quiz["question_count"] = self._question_count(quiz["id"])
            quiz["active_question_count"] = self._active_question_count(quiz["id"])
            result.append(quiz)
        return result

    def _active_question_count(self, quiz_id: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "select count(*) as c from questions where quiz_id = ? and enabled = 1",
                (quiz_id,),
            ).fetchone()
        return int(row["c"])

    def _question_count(self, quiz_id: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "select count(*) as c from questions where quiz_id = ?", (quiz_id,)
            ).fetchone()
        return int(row["c"])

    def set_quiz_deployed(self, quiz_id: str, deployed: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "update quizzes set deployed = ? where id = ?",
                (1 if deployed else 0, quiz_id),
            )

    def delete_quiz(self, quiz_id: str) -> None:
        with self._connect() as conn:
            conn.execute("delete from submission_answers where submission_id in (select id from submissions where quiz_id = ?)", (quiz_id,))
            conn.execute("delete from submissions where quiz_id = ?", (quiz_id,))
            conn.execute("delete from questions where quiz_id = ?", (quiz_id,))
            conn.execute("delete from quizzes where id = ?", (quiz_id,))

    def add_question(
        self,
        quiz_id: str,
        question_text: str,
        options: list[str],
        correct_index: int,
    ) -> dict[str, Any]:
        question_id = str(uuid.uuid4())
        sort_order = self._question_count(quiz_id)
        with self._connect() as conn:
            conn.execute(
                """
                insert into questions (id, quiz_id, sort_order, question_text, options, correct_index, enabled)
                values (?, ?, ?, ?, ?, ?, 1)
                """,
                (question_id, quiz_id, sort_order, question_text, json.dumps(options), correct_index),
            )
        return self._get_question(question_id)  # type: ignore[return-value]

    def _get_question(self, question_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("select * from questions where id = ?", (question_id,)).fetchone()
        if not row:
            return None
        return self._normalize_question(dict(row))

    def list_questions(self, quiz_id: str, *, active_only: bool = False) -> list[dict[str, Any]]:
        query = "select * from questions where quiz_id = ?"
        if active_only:
            query += " and enabled = 1"
        query += " order by sort_order"
        with self._connect() as conn:
            rows = conn.execute(query, (quiz_id,)).fetchall()
        return [self._normalize_question(dict(row)) for row in rows]

    def set_question_enabled(self, question_id: str, enabled: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "update questions set enabled = ? where id = ?",
                (1 if enabled else 0, question_id),
            )

    def delete_question(self, question_id: str) -> None:
        with self._connect() as conn:
            conn.execute("delete from questions where id = ?", (question_id,))

    def import_quiz_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = payload.get("title", "Imported Quiz")
        quiz = self.create_quiz(title)
        for item in payload.get("questions", []):
            self.add_question(
                quiz["id"],
                item["question_text"],
                item["options"],
                int(item["correct_index"]),
            )
        return quiz

    def submit_quiz(
        self,
        quiz_id: str,
        student_name: str,
        answers: dict[str, int],
    ) -> dict[str, Any]:
        questions = self.list_questions(quiz_id, active_only=True)
        if not questions:
            return {
                "id": "",
                "student_name": student_name.strip(),
                "score": 0,
                "total": 0,
            }
        score = 0
        submission_id = str(uuid.uuid4())
        with self._connect() as conn:
            for q in questions:
                selected = answers.get(q["id"])
                is_correct = selected is not None and selected == q["correct_index"]
                if is_correct:
                    score += 1
                conn.execute(
                    """
                    insert into submission_answers
                    (id, submission_id, question_id, selected_index, is_correct)
                    values (?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        submission_id,
                        q["id"],
                        selected if selected is not None else -1,
                        1 if is_correct else 0,
                    ),
                )
            conn.execute(
                """
                insert into submissions (id, quiz_id, student_name, score, total, submitted_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (submission_id, quiz_id, student_name.strip(), score, len(questions), _now_iso()),
            )
        return {
            "id": submission_id,
            "student_name": student_name.strip(),
            "score": score,
            "total": len(questions),
        }

    def list_submissions(self, quiz_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select * from submissions where quiz_id = ? order by submitted_at desc",
                (quiz_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_student(self, name: str, photo_bytes: bytes) -> dict[str, Any]:
        student_id = str(uuid.uuid4())
        compressed = compress_image(photo_bytes)
        filename = f"{student_id}.jpg"
        path = PHOTO_DIR / filename
        path.write_bytes(compressed)
        with self._connect() as conn:
            conn.execute(
                "insert into students (id, name, photo_path, created_at) values (?, ?, ?, ?)",
                (student_id, name.strip(), filename, _now_iso()),
            )
        return {"id": student_id, "name": name.strip(), "photo_path": filename}

    def list_students(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select * from students order by name collate nocase").fetchall()
        return [dict(row) for row in rows]

    def get_photo_bytes(self, photo_path: str) -> bytes | None:
        path = PHOTO_DIR / photo_path
        if path.exists():
            return path.read_bytes()
        return None


class SupabaseDatabase(Database):
    BUCKET = "student-photos"

    def __init__(self, url: str, key: str) -> None:
        from supabase import create_client

        self.client = create_client(url, key)

    @property
    def backend_name(self) -> str:
        return "Supabase"

    def create_quiz(self, title: str) -> dict[str, Any]:
        code = generate_quiz_code()
        while self.client.table("quizzes").select("id").eq("code", code).execute().data:
            code = generate_quiz_code()
        row = (
            self.client.table("quizzes")
            .insert({"title": title, "code": code, "deployed": False})
            .execute()
            .data[0]
        )
        return row

    def get_quiz(self, quiz_id: str) -> dict[str, Any] | None:
        data = self.client.table("quizzes").select("*").eq("id", quiz_id).execute().data
        return data[0] if data else None

    def get_quiz_by_code(self, code: str) -> dict[str, Any] | None:
        data = (
            self.client.table("quizzes")
            .select("*")
            .eq("code", code.strip().upper())
            .eq("deployed", True)
            .execute()
            .data
        )
        return data[0] if data else None

    def list_quizzes(self) -> list[dict[str, Any]]:
        quizzes = self.client.table("quizzes").select("*").order("created_at", desc=True).execute().data
        for quiz in quizzes:
            count = (
                self.client.table("questions")
                .select("id", count="exact")
                .eq("quiz_id", quiz["id"])
                .execute()
            )
            quiz["question_count"] = count.count or 0
            active = (
                self.client.table("questions")
                .select("id", count="exact")
                .eq("quiz_id", quiz["id"])
                .eq("enabled", True)
                .execute()
            )
            quiz["active_question_count"] = active.count or 0
        return quizzes

    def set_quiz_deployed(self, quiz_id: str, deployed: bool) -> None:
        self.client.table("quizzes").update({"deployed": deployed}).eq("id", quiz_id).execute()

    def delete_quiz(self, quiz_id: str) -> None:
        self.client.table("quizzes").delete().eq("id", quiz_id).execute()

    def _normalize_question(self, row: dict[str, Any]) -> dict[str, Any]:
        q = dict(row)
        q["enabled"] = bool(q.get("enabled", True))
        return q

    def add_question(
        self,
        quiz_id: str,
        question_text: str,
        options: list[str],
        correct_index: int,
    ) -> dict[str, Any]:
        count = (
            self.client.table("questions")
            .select("id", count="exact")
            .eq("quiz_id", quiz_id)
            .execute()
        )
        row = (
            self.client.table("questions")
            .insert(
                {
                    "quiz_id": quiz_id,
                    "sort_order": count.count or 0,
                    "question_text": question_text,
                    "options": options,
                    "correct_index": correct_index,
                    "enabled": True,
                }
            )
            .execute()
            .data[0]
        )
        return self._normalize_question(row)

    def list_questions(self, quiz_id: str, *, active_only: bool = False) -> list[dict[str, Any]]:
        query = (
            self.client.table("questions")
            .select("*")
            .eq("quiz_id", quiz_id)
            .order("sort_order")
        )
        if active_only:
            query = query.eq("enabled", True)
        rows = query.execute().data or []
        return [self._normalize_question(row) for row in rows]

    def set_question_enabled(self, question_id: str, enabled: bool) -> None:
        self.client.table("questions").update({"enabled": enabled}).eq("id", question_id).execute()

    def delete_question(self, question_id: str) -> None:
        self.client.table("questions").delete().eq("id", question_id).execute()

    def import_quiz_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        quiz = self.create_quiz(payload.get("title", "Imported Quiz"))
        for item in payload.get("questions", []):
            self.add_question(
                quiz["id"],
                item["question_text"],
                item["options"],
                int(item["correct_index"]),
            )
        return quiz

    def submit_quiz(
        self,
        quiz_id: str,
        student_name: str,
        answers: dict[str, int],
    ) -> dict[str, Any]:
        questions = self.list_questions(quiz_id, active_only=True)
        score = sum(
            1
            for q in questions
            if answers.get(q["id"]) is not None and answers[q["id"]] == q["correct_index"]
        )
        submission = (
            self.client.table("submissions")
            .insert(
                {
                    "quiz_id": quiz_id,
                    "student_name": student_name.strip(),
                    "score": score,
                    "total": len(questions),
                }
            )
            .execute()
            .data[0]
        )
        answer_rows = []
        for q in questions:
            selected = answers.get(q["id"])
            is_correct = selected is not None and selected == q["correct_index"]
            answer_rows.append(
                {
                    "submission_id": submission["id"],
                    "question_id": q["id"],
                    "selected_index": selected if selected is not None else -1,
                    "is_correct": is_correct,
                }
            )
        if answer_rows:
            self.client.table("submission_answers").insert(answer_rows).execute()
        return submission

    def list_submissions(self, quiz_id: str) -> list[dict[str, Any]]:
        return (
            self.client.table("submissions")
            .select("*")
            .eq("quiz_id", quiz_id)
            .order("submitted_at", desc=True)
            .execute()
            .data
        )

    def add_student(self, name: str, photo_bytes: bytes) -> dict[str, Any]:
        student_id = str(uuid.uuid4())
        compressed = compress_image(photo_bytes)
        filename = f"{student_id}.jpg"
        self.client.storage.from_(self.BUCKET).upload(
            filename,
            compressed,
            {"content-type": "image/jpeg", "upsert": "true"},
        )
        row = (
            self.client.table("students")
            .insert({"name": name.strip(), "photo_path": filename})
            .execute()
            .data[0]
        )
        return row

    def list_students(self) -> list[dict[str, Any]]:
        return (
            self.client.table("students")
            .select("*")
            .order("name")
            .execute()
            .data
        )

    def get_photo_bytes(self, photo_path: str) -> bytes | None:
        try:
            return self.client.storage.from_(self.BUCKET).download(photo_path)
        except Exception:
            return None


def question_enabled(question: dict[str, Any]) -> bool:
    return bool(question.get("enabled", True))


def get_database() -> Database:
    if "laos_database" not in st.session_state:
        try:
            url = st.secrets.get("supabase_url", "")
            key = st.secrets.get("supabase_key", "")
        except Exception:
            url = ""
            key = ""

        if url and key:
            st.session_state.laos_database = SupabaseDatabase(url, key)
        else:
            st.session_state.laos_database = LocalDatabase()
    return st.session_state.laos_database
