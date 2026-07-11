def format_history(history: list) -> str:
    if not history:
        return "لا توجد محادثة سابقة."

    formatted = []
    for turn in history[-6:]:
        role = "المستخدم" if turn["role"] == "user" else "المساعد"
        formatted.append(f"{role}: {turn['content']}")

    return "\n".join(formatted)


def add_to_history(history: list, question: str, answer: str) -> list:
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    return history


def trim_history(history: list, max_turns: int = 10) -> list:
    if len(history) > max_turns * 2:
        return history[-(max_turns * 2):]
    return history