# CrewAI Build Report

**Name:** Venkata Shanmukha Sathwik Atchutuni
**Topic I used:** how small teams can use AI agents in data science

## 1. What I changed
I changed the voice of the Technical Writer agent. In `crewai-kit/main.py`, I edited the `writer = Agent(...)` definition (lines 40-41):

- `goal`: from "Explain {topic} to a smart reader outside the field" to "Explain {topic} to a curious 10-year-old"
- `backstory`: from "You turn dense technical material into clear, jargon-free prose." to "You write for curious 10-year-olds: short sentences, everyday examples like school, games, and sports, and you explain any big word the first time you use it."

I changed the goal as well as the backstory because keeping the old goal would have given the Writer two conflicting audiences, which could weaken the effect and make the result harder to interpret. I chose this change because it should produce a difference anyone can see in the text, and because it tests how much an agent's backstory, which becomes part of its system prompt, actually controls what it writes. I left the Research Analyst, the Editor, all three tasks, and the topic unchanged, so that any difference between the runs would come from this one edit.


## 2. How CrewAI works
CrewAI builds a workflow from three pieces. An **agent** is a role-playing LLM persona defined by a `role`, a `goal`, and a `backstory`; CrewAI turns these into the agent's system prompt, so they shape how it thinks and writes. A **task** is a unit of work with a `description`, an `expected_output` that defines what "done" looks like, and the agent responsible for it. A **crew** combines agents and tasks and decides how they run. This kit uses `Process.sequential`, so tasks run in order and each task receives the previous task's output as context: the Research Analyst's brief goes to the Technical Writer, and the Writer's draft goes to the Editor. The `{topic}` placeholders are filled in by `crew.kickoff(inputs={"topic": ...})`.

My change worked because the Writer's goal and backstory are part of its prompt. Telling it the reader was a 10-year-old changed what it treated as a good answer, so it switched to everyday analogies and added plain definitions of technical terms. However, in a sequential crew the final output is whatever the last task returns. The Editor's goal ("tighten the draft and flag any claim that needs a source") and backstory ("cut filler") said nothing about the audience, so it treated the analogies as filler and rewrote the draft in adult prose. Each agent only follows its own prompt. Nothing in the crew carries the Writer's audience forward unless a later agent or task is explicitly told about it.

## 3. Evidence
In run 1 (`run1_original.txt`, `explainer_run1.md`), the Technical Writer produced a standard adult explainer ("Small data-science teams can stretch their limited time and budget..."), and the Editor tightened it and added [source needed] flags.

In run 2 (`run2_changed.txt`), the Writer's "Agent Final Answer" panel is completely different. It opens with "Imagine a small soccer team that wants to win a tournament," uses analogies such as a robot coach, tying shoelaces, and borrowing a bike instead of buying one, and defines terms in parentheses, for example "automate (do automatically)," "data-lineage graphs (maps that show where data came from)," and "hallucinations (imagining wrong things)." This matches the new backstory closely.

However, `explainer_run2.md` reads like an adult explainer. The Editor removed the analogies and definitions and reorganized the text into bold-headed points (Automation, Low-code/no-code interfaces, Cost-effective compute, Automatic documentation, Risk of hallucination and bias). So the clearest evidence of my change is the Writer's panel in `run2_changed.txt`, not the final file. The two final explainers also differ because the Research Analyst produced different "facts" in each run even though I did not change it, so comparing only the final files would mix my change with random variation.

What went wrong: my first attempt at run 2 failed. The Research Analyst finished, but the Writer received an empty reply from the Groq model three times ("Invalid response from LLM call - None or empty"), and CrewAI stopped the crew. Because it stopped early, `explainer.md` was not overwritten. I waited about a minute and re-ran the same command, and it completed. This looked like a temporary model-side issue, possibly from running two crews back to back.


## 4. Choosing a framework
CrewAI suits a project like this because the work splits naturally into roles with hand-offs: research, then writing, then editing. I could describe each role in plain language, and changing the crew's behavior meant editing one sentence of a backstory rather than changing any control flow. Process.sequential handled passing each output to the next agent for me, which made CrewAI the quickest way to get a multi-role pipeline running. The trade-offs are a heavy install (about 770 MB) and the fact that most control happens through prompts.

My experiment exposed that limitation. I wanted the 10-year-old audience to survive to the final output, but in CrewAI I could only influence the Editor by rewriting its prompt. With LangGraph, I would define the state myself, so I could include an explicit "audience" field that every node reads. I could also add a check node after the editor with a conditional edge that loops back if the text is not written for a 10-year-old, or use interrupt_before to pause for human approval before finishing. That would make the behavior more controllable and easier to audit. The cost is more code: I would have to write the state, nodes, and edges myself instead of listing agents and tasks, so LangGraph would be harder to start with but better once the workflow needs guarantees.


## 5. Verification and AI use
Verification: The kit has no web access, so every fact in the output comes from the model's memory, and I treated all of it as unverified. My runs show why. The Research Analyst was unchanged and the topic was identical, yet the two runs produced completely different statistics: run 1 cited an AWS case study (30% compute savings), a 2022 Kaggle team, and a 2024 NIST survey (22%), while run 2 cited a "3-5x faster" benchmark from a NeurIPS 2023 paper, an "under $15" project cost, an 80% documentation reduction, and a 7-12% error rate. I have not verified any of these, and the fact that they change from run to run suggests many are invented. The Editor's [source needed] flags helped but were not complete: in run 1 it left the AWS 30% claim unflagged. To check that my change worked, I compared the Writer's panels in both terminal logs against the new backstory and confirmed the analogies and plain-language definitions appeared only in run 2.

AI use: I used Claude (Anthropic) to guide me through installing the kits on Windows, troubleshoot folder and file-saving problems, suggest the find-and-replace edit to `main.py`, interpret the empty-response error, and draft an initial version of this report from my run logs. I verified this help by running both versions myself, checking the edited lines in `main.py`, comparing every claim in this report against my own terminal logs, and revising the wording.