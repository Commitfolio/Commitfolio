import type { FormEvent } from "react";
import { useState } from "react";

type RepositoryLookupFormProps = {
  error: string | null;
  state: "idle" | "loading" | "error";
  onLookupRepository: (value: string) => void;
};

export function RepositoryLookupForm({ error, state, onLookupRepository }: RepositoryLookupFormProps) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onLookupRepository(value);
  }

  return (
    <form className="repository-lookup" onSubmit={handleSubmit}>
      <label>
        <span>목록에 없으면 저장소 이름/URL로 직접 찾기</span>
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="SERVICE-MOHAENG/Mohaeng-BE 또는 GitHub URL"
          aria-label="저장소 직접 검색"
        />
      </label>
      <button className="button secondary" type="submit" disabled={state === "loading"}>
        {state === "loading" ? "저장소 찾는 중..." : "저장소 직접 찾기"}
      </button>
      {error ? <p className="notice error">{error}</p> : null}
    </form>
  );
}
