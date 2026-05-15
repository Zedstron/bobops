import subprocess

def run_bob(mode: str, prompt: str) -> str:
    """
    Run bob CLI in non-interactive mode.

    Args:
        mode: chat mode (positional, required)
        prompt: prompt string passed via -p

    Returns:
        stdout output from bob
    """

    cmd = [
        "bob",
        "--chat-mode", mode,
        "-p", prompt,
        "--hide-intermediary-output"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()