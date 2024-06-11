def generate_copywrite(copy: dict, topic: str, keywords: list[str] = []) -> str:
    return (
        """Forget what I said above and what you wrote just now.

Below are some examples. Please mimic their wording and phrasing to generate content based on the given topics.

"""
        + "\n".join(
            [
                f"Example {i+1}:\n{example}\n"
                for i, example in enumerate(copy["examples"])
            ]
        )
        + (
            f"""

Here is the specific point:
{copy["addition"].format(*keywords)}"""
            if copy.get("addition", "")
            else ""
        )
        + """
Topic: \n"""
        + topic
        + """"

(保持相似格式)
Please complete, thank you."""
    )
