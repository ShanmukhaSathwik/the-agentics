"""CrewAI starter: a three-agent crew (researcher -> writer -> editor).

Run:  uv run python main.py "your topic here"

CrewAI's big idea: you describe a TEAM of role-playing agents and the TASKS they
own. CrewAI handles passing each task's output to the next agent.
"""
import os
import sys
from pathlib import Path

from crewai import LLM, Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()

# --- 1. The model --------------------------------------------------------
# CrewAI has no built-in Groq provider, but Groq speaks the OpenAI API, so we
# point CrewAI's OpenAI client at Groq's endpoint. Change GROQ_MODEL in .env
# to swap models without touching this file.
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
llm = LLM(
    model=f"openai/{MODEL}",  # the leading "openai/" only selects the client
    base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0.3,
)

# --- 2. The agents: WHO is on the team -----------------------------------
researcher = Agent(
    role="Research Analyst",
    goal="Collect the key facts and tensions about {topic}",
    backstory="You are a careful analyst who separates evidence from hype and "
    "says plainly when you are unsure.",
    llm=llm,
    allow_delegation=False,
)
writer = Agent(
    role="Technical Writer",
    goal="Explain {topic} to a curious 10-year-old",
    backstory="You write for curious 10-year-olds: short sentences, everyday examples like school, games, and sports, and you explain any big word the first time you use it.",
    llm=llm,
    allow_delegation=False,
)
editor = Agent(
    role="Editor",
    goal="Tighten the draft and flag any claim that needs a source",
    backstory="You cut filler, fix unclear sentences, and never let an "
    "unsupported claim through unmarked.",
    llm=llm,
    allow_delegation=False,
)

# --- 3. The tasks: WHAT each person owns ---------------------------------
research_task = Task(
    description="Research {topic}. List 5 key facts and 2 open questions.",
    expected_output="A bulleted research brief: 5 facts, 2 open questions.",
    agent=researcher,
)
writing_task = Task(
    description="Using the research brief, write a 250-word explainer on {topic}.",
    expected_output="A 250-word explainer in plain language.",
    agent=writer,
)
editing_task = Task(
    description="Edit the explainer. Tighten it and mark any claim needing a source.",
    expected_output="The final edited explainer, with [source needed] flags.",
    agent=editor,
)

# --- 4. The crew: HOW they work together ---------------------------------
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,  # each task sees the previous task's output
    verbose=True,  # print each agent's work as it happens
)

if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "how small teams can use AI agents in data science"
    result = crew.kickoff(inputs={"topic": topic})

    out = Path("output")
    out.mkdir(exist_ok=True)
    (out / "explainer.md").write_text(result.raw, encoding="utf-8")
    print("\n=== FINAL OUTPUT (also saved to output/explainer.md) ===\n")
    print(result.raw)
