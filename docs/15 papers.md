1. Research Papers Reviewed (15)
1. Small Language Models are the Future of Agentic AI
This NVIDIA paper argues that most AI agents don't need a giant, general-purpose model at all - they just
repeat a small set of narrow tasks like calling tools, following formats, or writing short code snippets. A small
model (under about 10 billion parameters) can be trained to do those specific jobs just as well as a huge
model, while running 10-30 times cheaper, responding faster, and working fine on a regular laptop or
phone. The authors suggest the best design is a mix: small specialized models handle everyday tasks, and
a big model only gets called in for genuinely hard reasoning or open conversation.
Source: https://arxiv.org/abs/2506.02153
2. Small Language Models for Efficient Agentic Tool Calling: Outperforming Large
Models with Targeted Fine-tuning
This paper takes a small language model and fine-tunes it specifically to call tools and APIs correctly -
things like looking up data, running calculations, or triggering actions. After this targeted training, the small
model reached a 77.55% success rate on the ToolBench benchmark, beating much larger general-purpose
models at that specific job. It's solid proof that "smaller but specialized" can beat "bigger but generic" when
the task is narrow and well-defined.
Source: https://arxiv.org/abs/2512.15943
3. Advancing SLM Tool-Use Capability using Reinforcement Learning
This paper trains small language models (100 million to 5 billion parameters) to get better at using external
tools, using reinforcement learning instead of just standard fine-tuning. The point is that small models are
ideal for phones and edge devices because they need much less memory and power, and RL training helps
close the gap between what small models can do and what large models can do specifically on tool-calling
tasks.
Source: https://arxiv.org/abs/2509.04518
4. Beyond the Leaderboard: A Synthesis of Tool-Use, Planning, and Reasoning
Failures in Large Language Model Agents
Instead of introducing a new model, this Oxford paper reviews 27 other studies and benchmarks to build a
master list of the ways AI agents actually fail in the real world - bad planning, tool misuse, poor coordination
between steps, and reasoning breakdowns over long tasks. It's a useful reality check: benchmark scores
often hide these recurring failure patterns, so anyone building an agent should know what commonly goes
wrong before assuming their system is reliable.
Source: https://arxiv.org/abs/2607.05775
5. Large Language Models Cannot Self-Correct Reasoning Yet
This widely-cited paper tests whether an AI model can catch and fix its own mistakes just by re-reading and
reconsidering its own answer, with no outside help. The finding is that it generally can't - when a model tries
to "self-correct" without any external feedback (like a tool, a calculator, or another source of truth), its
answers often get worse, not better. This is a key lesson for anyone building a "self-checking AI" feature:
the checking needs to come from outside the model, not just from asking it to reflect on itself.
Source: https://arxiv.org/abs/2310.01798
6. CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing
This paper offers the fix to the problem in paper 5. Instead of asking a model to grade its own homework,
CRITIC has the model use real outside tools - a search engine to check facts, a code interpreter to check
math or code, a toxicity checker for harmful content - and then revise its answer based on what those tools
report back. Tested across fact-based Q&A;, math problems, and toxic content reduction, this "verify with
tools, then correct" loop reliably improved answers, while pure self-reflection without tools did not.
Source: https://arxiv.org/abs/2305.11738
7. ReVeal: Self-Evolving Code Agents via Reliable Self-Verification
This paper focuses on coding agents that write, test, and improve their own code over multiple rounds. The
key idea is "reliable self-verification" - instead of trusting the model's own opinion of whether its code works,
the system relies on things that can be checked objectively (like whether tests actually pass), which lets the
coding agent keep improving itself over time without a human watching every step.
Source: https://arxiv.org/abs/2506.11442
8. VerifiAgent: A Unified Verification Agent in Language Model Reasoning
VerifiAgent is a general-purpose "verification agent" designed to check the reasoning of other AI systems
across many different types of tasks (math, logic, general reasoning), rather than being built for just one
narrow use case. It gives fine-grained feedback pointing to exactly where a chain of reasoning went wrong,
rather than just a pass/fail judgment, which makes it more useful as a reusable "quality control" layer that
sits on top of any other AI agent.
Source: https://arxiv.org/abs/2504.00406
9. Enhancing LLM Planning Capabilities through Intrinsic Self-Critique
This paper digs into why AI models struggle to catch their own planning mistakes - for example, in
step-by-step task planning, models using only self-critique showed only modest improvement and produced
a lot of false positives, meaning they'd wrongly claim a broken plan was correct. The paper explores ways to
make this "self-critique" more reliable, which matters directly for the "third-person checker" pitch: naive
self-checking isn't good enough on its own.
Source: https://arxiv.org/abs/2512.24103
10. AgenTEE: Confidential LLM Agent Execution on Edge Devices
As more AI agents move from the cloud onto personal devices (phones, laptops) to improve speed and
privacy, a new problem appears: how do you keep the AI's system instructions, model files, and the user's
private data safe from other software or malicious users on that same device? AgenTEE solves this using
"confidential computing" - a secure, locked-off area of the device's hardware - so a locally-running AI agent
can process sensitive information without exposing it, even to other apps running on the same machine.
Source: https://arxiv.org/abs/2604.18231
11. Privacy in Action: Towards Realistic Privacy Mitigation and Evaluation for
LLM-Powered Agents
This paper points out that AI agents often say the right thing when asked directly about privacy, but leak
private information anyway when actually performing tasks (like summarizing conversations or automating
workflows across apps). The authors built a tool called PrivacyChecker that plugs into an agent's workflow
and cut privacy leaks dramatically - from around 36% down to about 7% on one model - without making the
agent noticeably less helpful. This is directly useful for any assistant that will be handling personal files,
messages, or automations on a user's behalf.
Source: https://arxiv.org/abs/2509.17488
12. Forget to Improve: On-Device LLM-Agent Continual Learning via
Budget-Curated Memory
Since phones and laptops have limited storage and memory, an AI agent running locally can't just
remember everything forever the way a cloud system might. This paper proposes a smart "memory budget"
approach - the agent keeps learning and improving from experience over time, but it selectively decides
what to forget so it stays useful without needing constant retraining or unlimited storage. This is relevant for
building a local assistant that gets smarter the more you use it, without needing a data center behind it.
Source: https://arxiv.org/abs/2606.25115
13. RouteLLM: Learning to Route LLMs with Preference Data
RouteLLM builds a lightweight "router" that looks at each incoming question and decides on the fly whether
it's simple enough for a cheap, fast model or complicated enough to need a stronger, more expensive one.
Trained on human preference data, this routing approach cut costs by more than half in some cases while
keeping response quality about the same - a direct blueprint for a system that "guides you to the right
specialized tool" instead of always using the biggest, most expensive model for every request.
Source: https://arxiv.org/abs/2406.18665
14. Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey
This is a broad survey covering all the different strategies researchers use to send a question to the "right"
AI model out of a pool of many models - based on how hard the question is, past user preferences,
uncertainty in the answer, or cost constraints. It concludes that a well-designed routing system, one that
picks the best specialist for each part of a task, can actually outperform even the single most powerful
individual model, which supports the idea of an assistant that acts like a mentor pointing users toward the
best specialized tool rather than trying to do everything itself.
Source: https://arxiv.org/abs/2603.04445
15. Universal Model Routing for Efficient LLM Inference
This paper tackles a practical routing problem: what if new AI models keep getting released that your router
has never seen before? UniRoute proposes a routing method that can generalize to new, previously unseen
models without needing to be retrained from scratch every time, and it was tested successfully across more
than 30 different models it hadn't specifically trained on. This matters for any "aggregator" assistant meant
to keep working well even as the landscape of available AI tools keeps changing.
Source: https://arxiv.org/abs/2502.08773
2. Research Gap
Gap 1 - No combined system.
No prior work combines routing, local small models, and tool-based verification into one working system.
NVIDIA's SLM paper is a position paper with no shipped product; RouteLLM and UniRoute route between
models but were never tested for picking specialized tools (image gen, code exec, etc.); CRITIC's
verify-then-correct loop was only tested on large cloud models. No study has combined all three.
Gap 2 - Self-verification untested on small/local models.
CRITIC and VerifiAgent assume a fairly capable model doing the checking. Since small models reason
more weakly, it is unknown whether tool-grounded self-correction still works reliably at that scale, or breaks
down.
Gap 3 - Privacy safeguards assume special hardware.
AgenTEE requires a secure hardware enclave (TEE) that most consumer laptops do not have.
PrivacyChecker's leak-reduction result (36% to 7%) was only tested on large cloud models. No
software-only privacy safeguard has been shown for a lightweight local agent.
Gap 4 - No real desktop deployment.
Most papers evaluate only on academic benchmarks (e.g. ToolBench), not on a real, zero-setup desktop
application that a regular user can download and use.
Chosen focus: Gap 1 and Gap 2 combined - does tool-grounded self-verification improve routing
accuracy/reliability when the executor is a small local model? This is novel, testable within a two-semester
timeline, and builds directly on the identified gaps

references:
[1] Peter Belcak, Greg Heinrich, Shizhe Diao, Yonggan Fu, Xin Dong, Saurav Muralidharan, Yingyan Celine Lin, and Pavlo Molchanov, "Small Language Models are the Future of Agentic AI," arXiv:2506.02153, 2025.
[2] Polaris Jhandi, Owais Kazi, Shreyas Subramanian, and Neel Sendas, "Small Language Models for Efficient Agentic Tool Calling: Outperforming Large Models with Targeted Fine-tuning," arXiv:2512.15943, 2025.
[3] Dhruvi Paprunia, Pankti Doshi, and Vansh Kharidia, "Advancing SLM Tool-Use Capability using Reinforcement Learning," arXiv:2509.04518, 2025.
[4] Wael Albayaydh, Rui Zhao, and Ivan Flechais, "Beyond the Leaderboard: A Synthesis of Tool-Use, Planning, and Reasoning Failures in Large Language Model Agents," arXiv:2607.05775, 2026.
[5] Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, and Denny Zhou, "Large Language Models Cannot Self-Correct Reasoning Yet," arXiv:2310.01798, 2023.
[6] Zhibin Gou, Zhihong Shao, Yeyun Gong, Yelong Shen, Yujiu Yang, Nan Duan, and Weizhu Chen, "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing," arXiv:2305.11738, 2023.
[7] Yiyang Jin, Kunzhao Xu, Hang Li, Xueting Han, Yanmin Zhou, Cheng Li, and Jing Bai, "ReVeal: Self-Evolving Code Agents via Reliable Self-Verification," arXiv:2506.11442, 2025.
[8] Jiuzhou Han, Wray Buntine, and Ehsan Shareghi, "VerifiAgent: A Unified Verification Agent in Language Model Reasoning," arXiv:2504.00406, 2025.
[9] Bernd Bohnet, Pierre-Alexandre Kamienny, Hanie Sedghi, Dilan Gorur, Pranjal Awasthi, Aaron Parisi, Kevin Swersky, Rosanne Liu, Azade Nova, and Noah Fiedel, "Enhancing LLM Planning Capabilities through Intrinsic Self-Critique," arXiv:2512.24103, 2025.
[10] Sina Abdollahi, Mohammad M. Maheri, Javad Forough, Amir Al Sadi, Josh Millar, David Kotz, Marios Kogias, and Hamed Haddadi, "AgenTEE: Confidential LLM Agent Execution on Edge Devices," arXiv:2604.18231, 2026.
[11] Shouju Wang, Fenglin Yu, Xirui Liu, Xiaoting Qin, Jue Zhang, Qingwei Lin, Dongmei Zhang, and Saravan Rajmohan, "Privacy in Action: Towards Realistic Privacy Mitigation and Evaluation for LLM-Powered Agents," arXiv:2509.17488, 2025.
[12] Beining Wu, Zihao Ding, Jun Huang, and Yanxiao Zhao, "Forget to Improve: On-Device LLM-Agent Continual Learning via Budget-Curated Memory," arXiv:2606.25115, 2026.
[13] Isaac Ong, Amjad Almahairi, Vincent Wu, Wei-Lin Chiang, Tianhao Wu, Joseph E. Gonzalez, M. Waleed Kadous, and Ion Stoica, "RouteLLM: Learning to Route LLMs with Preference Data," arXiv:2406.18665, 2024.
[14] Yasmin Moslem and John D. Kelleher, "Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey," arXiv:2603.04445, 2026.
[15] Wittawat Jitkrittum, Harikrishna Narasimhan, Ankit Singh Rawat, Jeevesh Juneja, Zifeng Wang, Chen-Yu Lee, Pradeep Shenoy, Rina Panigrahy, Aditya Krishna Menon, and Sanjiv Kumar, "Universal Model Routing for Efficient LLM Inference," arXiv:2502.08773, 2025.