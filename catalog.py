"""
catalog.py — Realistic UVA course catalog (mock data).

90 courses across 12 departments.  Each record mirrors what you'd scrape from
Lou's List / the UVA course catalog, augmented with synthetic student-review
snippets and workload estimates to give the embedder richer signal.

In production this module would be replaced by scraper.py output.
"""

COURSES = [

    # ══════════════════════════════════════════════════════════════════════════
    # COMPUTER SCIENCE
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "CS1110",
        "mnemonic": "CS", "number": 1110,
        "title": "Introduction to Programming",
        "description": (
            "A first course in programming using Python. Covers variables, data types, "
            "conditionals, loops, functions, lists, dictionaries, file I/O, and object-oriented "
            "programming basics. Students complete weekly lab assignments building small "
            "applications such as image filters, text analyzers, and simple games. "
            "No prior programming experience required — this course is the standard entry "
            "point for CS majors and students across the University who want to learn to code. "
            "Python is used throughout industry and academia for data science, automation, "
            "scripting, and rapid prototyping."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "09:00", "end": "09:50", "instructor": "Tychonievich, L."},
            {"section": "002", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Basit, N."},
            {"section": "003", "days": ["Mon","Wed","Fri"], "start": "13:00", "end": "13:50", "instructor": "Cohoon, J."},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["python","programming","beginner","coding","intro","software","scripting","loops","functions","object-oriented"],
        "reviews": "Great starting point. Professor explains everything clearly. Homeworks are reasonable.",
    },
    {
        "id": "CS2100",
        "mnemonic": "CS", "number": 2100,
        "title": "Data Structures and Algorithms 1",
        "description": (
            "Fundamental data structures including arrays, linked lists, stacks, queues, "
            "binary trees, heaps, and hash tables. Algorithm analysis with Big-O notation. "
            "Students implement all structures from scratch in Java and analyze their "
            "time and space complexity. Covers sorting algorithms (merge, quick, heap sort), "
            "binary search, and basic graph representations. "
            "This course is the backbone of technical coding interviews at software companies "
            "like Google, Meta, Amazon, and Microsoft. Strong emphasis on problem-solving "
            "and writing clean, efficient code."
        ),
        "credits": 3, "prereqs": ["CS1110"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "14:00", "end": "15:15", "instructor": "Floryan, M."},
            {"section": "002", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Nguyen, C."},
        ],
        "difficulty": 4, "workload_hrs_week": 12,
        "tags": ["data structures","algorithms","java","Big-O","trees","linked lists","sorting","hash tables","coding interviews","problem solving"],
        "reviews": "Challenging but essential. Floryan is excellent. Prepares you well for internship interviews.",
    },
    {
        "id": "CS2120",
        "mnemonic": "CS", "number": 2120,
        "title": "Discrete Mathematics and Theory 1",
        "description": (
            "Mathematical foundations of computer science. Topics include propositional and "
            "predicate logic, proof techniques (direct, contradiction, induction), set theory, "
            "relations, functions, combinatorics, and probability. Students learn to read and "
            "write rigorous mathematical proofs. "
            "This course is the theoretical foundation for algorithms, programming languages, "
            "cryptography, and machine learning. Essential for anyone who wants to go to "
            "graduate school or work on research-level problems in CS."
        ),
        "credits": 3, "prereqs": ["CS1110"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Luther, K."},
        ],
        "difficulty": 4, "workload_hrs_week": 9,
        "tags": ["discrete math","logic","proofs","induction","combinatorics","theory","formal reasoning","sets","probability"],
        "reviews": "Hardest course for many CS majors. Stick with it — the proof skills pay off everywhere.",
    },
    {
        "id": "CS2130",
        "mnemonic": "CS", "number": 2130,
        "title": "Computer Systems and Organization",
        "description": (
            "How computers work from the ground up: binary and hexadecimal number systems, "
            "Boolean logic, assembly language (x86-64), C programming, memory management "
            "with pointers and malloc, the stack and heap, process management, and the "
            "Linux command line. Students build a virtual machine and write a tiny C compiler. "
            "Understanding systems is critical for writing performant software, debugging hard "
            "bugs, working with embedded systems, and understanding security vulnerabilities. "
            "Favorite among students going into systems, security, or low-level engineering."
        ),
        "credits": 3, "prereqs": ["CS2100"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Brunelle, N."},
        ],
        "difficulty": 4, "workload_hrs_week": 12,
        "tags": ["systems","C","assembly","memory","pointers","x86","Linux","low-level","embedded","operating systems","performance"],
        "reviews": "Genuinely eye-opening — finally understand what's happening under the hood.",
    },
    {
        "id": "CS3130",
        "mnemonic": "CS", "number": 3130,
        "title": "Theory of Computation",
        "description": (
            "Formal models of computation: finite automata and regular languages, pushdown automata "
            "and context-free grammars, Turing machines, decidability, the halting problem, "
            "and computational complexity classes P, NP, and NP-completeness. "
            "Students prove fundamental limitations of what computers can and cannot compute. "
            "Essential preparation for graduate-level CS, programming language research, "
            "and compiler design. "
            "Abstract and proof-heavy — students who loved Discrete Math will thrive here."
        ),
        "credits": 3, "prereqs": ["CS2120","CS2100"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "11:00", "end": "11:50", "instructor": "Horton, T."},
        ],
        "difficulty": 5, "workload_hrs_week": 10,
        "tags": ["theory","automata","Turing machines","NP-completeness","computability","formal languages","proofs","complexity","P vs NP"],
        "reviews": "Most abstract CS course. Very difficult but extremely satisfying if you enjoy theory.",
    },
    {
        "id": "CS3140",
        "mnemonic": "CS", "number": 3140,
        "title": "Software Development Essentials",
        "description": (
            "Professional software engineering practices for building large, maintainable systems. "
            "Covers design patterns (SOLID, MVC, factory, observer), unit and integration testing "
            "with JUnit, version control with Git, agile and Scrum methodologies, CI/CD pipelines, "
            "refactoring, and code reviews. Students work in teams of 4–5 on a semester-long "
            "Java project simulating a real startup environment. "
            "This course bridges the gap between 'writing code' and 'building software products.' "
            "Highly relevant for software engineering internships and full-time roles."
        ),
        "credits": 3, "prereqs": ["CS2100"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "15:30", "end": "16:45", "instructor": "McBurney, P."},
        ],
        "difficulty": 3, "workload_hrs_week": 10,
        "tags": ["software engineering","design patterns","testing","java","agile","scrum","git","teamwork","product development","CI/CD","refactoring"],
        "reviews": "Best team project course in the department. Prepares you for real software jobs.",
    },
    {
        "id": "CS3240",
        "mnemonic": "CS", "number": 3240,
        "title": "Advanced Software Development",
        "description": (
            "Full-stack web development in a team setting. Students build and deploy a real "
            "web application using Django (Python), PostgreSQL, and cloud hosting on Heroku or AWS. "
            "Topics include RESTful API design, OAuth2 authentication, database migrations, "
            "containerization with Docker, and software security basics. "
            "Each team ships a live, publicly accessible product by the end of the semester. "
            "This is the most project-heavy course in the CS curriculum and the best preparation "
            "for software engineering internships at tech companies."
        ),
        "credits": 3, "prereqs": ["CS3140"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "11:00", "end": "12:15", "instructor": "Sherriff, M."},
        ],
        "difficulty": 4, "workload_hrs_week": 15,
        "tags": ["web development","django","python","full-stack","REST API","database","Docker","AWS","cloud","deployment","team project","software engineering"],
        "reviews": "Exhausting but you come out with a real product in your portfolio. Essential for SWE internships.",
    },
    {
        "id": "CS4102",
        "mnemonic": "CS", "number": 4102,
        "title": "Algorithms",
        "description": (
            "Advanced design and analysis of algorithms. Topics: divide-and-conquer, dynamic "
            "programming, greedy algorithms, graph algorithms (Dijkstra, Bellman-Ford, max flow), "
            "amortized analysis, randomized algorithms, and reductions to prove NP-completeness. "
            "Students learn to design efficient algorithms for new problems and formally prove "
            "their correctness and running time. "
            "Required for most CS graduate programs and heavily tested in software engineering "
            "interviews at top tech companies. "
            "Proof-heavy — mathematical maturity from Discrete Math is essential."
        ),
        "credits": 3, "prereqs": ["CS2100","CS2120"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Horton, T."},
            {"section": "002", "days": ["Mon","Wed","Fri"], "start": "12:00", "end": "12:50", "instructor": "Wu, C."},
        ],
        "difficulty": 5, "workload_hrs_week": 12,
        "tags": ["algorithms","dynamic programming","greedy","graph algorithms","NP-completeness","proofs","Dijkstra","complexity","interview prep","FAANG"],
        "reviews": "Hardest core course. Dynamic programming section is brutal but worth mastering.",
    },
    {
        "id": "CS4414",
        "mnemonic": "CS", "number": 4414,
        "title": "Operating Systems",
        "description": (
            "Deep dive into operating system design and implementation. Covers processes and threads, "
            "CPU scheduling, memory management and virtual memory, file systems, I/O subsystems, "
            "concurrency, synchronization primitives (mutexes, semaphores, condition variables), "
            "and deadlock. Students implement a kernel thread scheduler and a virtual memory "
            "system in C. "
            "Invaluable for systems programmers, embedded engineers, cloud infrastructure roles, "
            "and anyone working close to hardware. Heavy C and Linux programming."
        ),
        "credits": 3, "prereqs": ["CS2130"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "14:00", "end": "14:50", "instructor": "Veeraraghavan, M."},
        ],
        "difficulty": 5, "workload_hrs_week": 14,
        "tags": ["operating systems","kernel","processes","threads","concurrency","memory management","file systems","C","Linux","systems programming","scheduling","deadlock"],
        "reviews": "Hardest course I've taken. The kernel projects are painful but I learned so much.",
    },
    {
        "id": "CS4457",
        "mnemonic": "CS", "number": 4457,
        "title": "Computer Networks",
        "description": (
            "Principles and implementation of computer networks. The TCP/IP protocol stack from "
            "physical layer to application layer: Ethernet, IP routing, TCP flow and congestion "
            "control, DNS, HTTP/2, TLS, and content delivery networks. Students implement "
            "a reliable transport protocol over UDP and build a simple HTTP server. "
            "Highly relevant for cloud computing, distributed systems, cybersecurity, "
            "and backend engineering. "
            "Essential background for understanding how the modern internet actually works."
        ),
        "credits": 3, "prereqs": ["CS2130"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Veeraraghavan, M."},
        ],
        "difficulty": 4, "workload_hrs_week": 11,
        "tags": ["networking","TCP/IP","HTTP","DNS","TLS","distributed systems","cloud","internet","protocols","security","backend","sockets"],
        "reviews": "Finally understand the internet. Socket programming projects are challenging but fun.",
    },
    {
        "id": "CS4501-ML",
        "mnemonic": "CS", "number": 4501,
        "title": "Machine Learning",
        "description": (
            "Mathematical foundations and practical techniques of machine learning. Supervised "
            "learning: linear and logistic regression, SVMs, decision trees, random forests, "
            "gradient boosting. Unsupervised learning: k-means, hierarchical clustering, PCA. "
            "Neural networks: backpropagation, convolutional networks, training tricks. "
            "Students implement algorithms from scratch in Python/NumPy, then use PyTorch for "
            "deep learning experiments on real datasets (MNIST, CIFAR, text corpora). "
            "Bridges theory (optimization, probability) and practice. "
            "One of the most popular electives in the department for students interested in AI."
        ),
        "credits": 3, "prereqs": ["CS2100","MATH3351"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "11:00", "end": "11:50", "instructor": "Hua, Y."},
        ],
        "difficulty": 4, "workload_hrs_week": 12,
        "tags": ["machine learning","AI","neural networks","deep learning","pytorch","scikit-learn","python","classification","regression","clustering","PCA","SVM","random forests"],
        "reviews": "Best ML course at UVA. Hua is an amazing lecturer. Homeworks are hard but very educational.",
    },
    {
        "id": "CS4774",
        "mnemonic": "CS", "number": 4774,
        "title": "Natural Language Processing",
        "description": (
            "Text processing, language modeling, and modern NLP systems. Classical methods: "
            "tokenization, n-gram models, TF-IDF, named entity recognition, POS tagging. "
            "Modern deep learning: word embeddings (Word2Vec, GloVe), recurrent networks (LSTMs), "
            "the transformer architecture, BERT, GPT-style models, and instruction tuning. "
            "Students fine-tune pre-trained language models on downstream tasks (sentiment "
            "analysis, question answering, summarization) using HuggingFace Transformers. "
            "Directly relevant to careers at AI companies building chatbots, search engines, "
            "and generative AI products. Prerequisite: Machine Learning."
        ),
        "credits": 3, "prereqs": ["CS4501-ML"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Ji, H."},
        ],
        "difficulty": 4, "workload_hrs_week": 13,
        "tags": ["NLP","natural language processing","language models","transformers","BERT","GPT","LLMs","HuggingFace","chatbots","text mining","AI","sentiment analysis","question answering","generative AI"],
        "reviews": "If you want to work on ChatGPT-style systems, take this class. Very current material.",
    },
    {
        "id": "CS4501-CV",
        "mnemonic": "CS", "number": 4501,
        "title": "Computer Vision",
        "description": (
            "Computational methods for understanding images and video. Image formation, filtering, "
            "edge and keypoint detection, camera calibration, stereo vision, optical flow, "
            "and 3D reconstruction. Deep learning for vision: convolutional networks, "
            "object detection (YOLO, Faster R-CNN), semantic segmentation, image generation "
            "with diffusion models. Students complete a final project on a real-world vision task. "
            "Relevant to robotics, autonomous vehicles, medical imaging, augmented reality, "
            "and AI creative tools. PyTorch-based."
        ),
        "credits": 3, "prereqs": ["CS4501-ML"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "15:30", "end": "16:45", "instructor": "Daume, H."},
        ],
        "difficulty": 4, "workload_hrs_week": 12,
        "tags": ["computer vision","image processing","deep learning","CNN","object detection","segmentation","diffusion models","robotics","autonomous vehicles","pytorch","AI"],
        "reviews": "Amazing course if you're into visual AI. The final project is a highlight.",
    },
    {
        "id": "CS4750",
        "mnemonic": "CS", "number": 4750,
        "title": "Database Systems",
        "description": (
            "Design and internals of relational database systems. Relational algebra, SQL (joins, "
            "aggregates, subqueries, window functions), query optimization and execution plans, "
            "B-tree indexes, normalization (1NF–BCNF), transactions, ACID properties, concurrency "
            "control (2PL, MVCC), and crash recovery. Also covers NoSQL systems: document stores "
            "(MongoDB), key-value stores, and columnar databases. "
            "Students build a simplified query executor as the main project. "
            "Essential for backend engineers, data engineers, and anyone building data-intensive "
            "applications."
        ),
        "credits": 3, "prereqs": ["CS2100"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "15:30", "end": "16:45", "instructor": "Alawini, A."},
        ],
        "difficulty": 3, "workload_hrs_week": 10,
        "tags": ["databases","SQL","NoSQL","PostgreSQL","MongoDB","query optimization","transactions","ACID","data engineering","backend","B-trees","normalization"],
        "reviews": "Incredibly practical. I use SQL every day at my internship now.",
    },
    {
        "id": "CS3710",
        "mnemonic": "CS", "number": 3710,
        "title": "Introduction to Cybersecurity",
        "description": (
            "Foundational concepts in computer and network security. Cryptography: symmetric ciphers "
            "(AES), public-key cryptography (RSA, elliptic curves), hash functions, digital signatures. "
            "Authentication and authorization, web security (XSS, SQL injection, CSRF), "
            "binary exploitation (buffer overflows, format strings), network attacks and defenses, "
            "malware analysis, and security policy. "
            "Weekly CTF-style labs provide hands-on hacking experience in a safe environment. "
            "Great entry point for students interested in penetration testing, security engineering, "
            "or government/defense work."
        ),
        "credits": 3, "prereqs": ["CS2130"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "11:00", "end": "12:15", "instructor": "Evans, D."},
        ],
        "difficulty": 3, "workload_hrs_week": 9,
        "tags": ["cybersecurity","hacking","cryptography","CTF","web security","buffer overflow","penetration testing","network security","malware","SQL injection","XSS","ethical hacking"],
        "reviews": "Most fun labs in the department. CTF challenges are addictive.",
    },
    {
        "id": "CS4810",
        "mnemonic": "CS", "number": 4810,
        "title": "Computer Graphics",
        "description": (
            "Theory and practice of real-time and offline rendering. Rasterization pipeline, "
            "ray tracing and path tracing, shading models (Phong, PBR), texture mapping, "
            "shadow algorithms, global illumination, and GPU programming with OpenGL and GLSL. "
            "Students build a software rasterizer and a ray tracer from scratch, then use "
            "WebGL for a final creative project. "
            "Ideal for students interested in game development, VFX, simulation, "
            "scientific visualization, or building graphics engines. "
            "Heavy linear algebra and mathematical reasoning required."
        ),
        "credits": 3, "prereqs": ["CS2100","MATH3351"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "12:30", "end": "13:45", "instructor": "Evangelista, P."},
        ],
        "difficulty": 4, "workload_hrs_week": 12,
        "tags": ["graphics","rendering","ray tracing","OpenGL","GPU","game development","shading","rasterization","3D","WebGL","visual computing","linear algebra"],
        "reviews": "If you love games or visual things, this course is a dream. Projects look amazing.",
    },
    {
        "id": "CS4720",
        "mnemonic": "CS", "number": 4720,
        "title": "Mobile Application Development",
        "description": (
            "Design and development of native mobile applications for iOS (Swift) and Android (Kotlin/Jetpack). "
            "UI design patterns, lifecycle management, persistent storage, RESTful API consumption, "
            "push notifications, sensors and location services, and app store submission. "
            "Students ship a fully functional iOS or Android app as their final project. "
            "Highly practical course — students leave with a polished app in their portfolio. "
            "Great for students interested in consumer tech, startups, or mobile platforms."
        ),
        "credits": 3, "prereqs": ["CS3140"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Sherriff, M."},
        ],
        "difficulty": 3, "workload_hrs_week": 11,
        "tags": ["mobile","iOS","Android","Swift","Kotlin","app development","UI","startups","consumer tech","portfolio","REST API"],
        "reviews": "Walked out with a real app on the App Store. Super motivating course.",
    },
    {
        "id": "CS4640",
        "mnemonic": "CS", "number": 4640,
        "title": "Programming Languages",
        "description": (
            "Principles underlying programming language design and implementation. Syntax and semantics, "
            "type systems and type inference, functional programming in Haskell and OCaml, "
            "lambda calculus, garbage collection, parameter passing mechanisms, and concurrency models. "
            "Students implement an interpreter for a small functional language. "
            "Changes how you think about programming — students report writing better code in "
            "every language after this class. "
            "Essential for compiler engineers, language designers, and PL researchers."
        ),
        "credits": 3, "prereqs": ["CS2120","CS2130"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Weimer, W."},
        ],
        "difficulty": 4, "workload_hrs_week": 10,
        "tags": ["programming languages","functional programming","Haskell","type systems","compilers","lambda calculus","interpreters","OCaml","language design"],
        "reviews": "Changed how I think about code. Hard, but every programmer should take this.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ELECTRICAL & COMPUTER ENGINEERING
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "ECE2330",
        "mnemonic": "ECE", "number": 2330,
        "title": "Digital Logic Design",
        "description": (
            "Boolean algebra, logic gates, combinational circuits (adders, multiplexers, decoders), "
            "sequential circuits (flip-flops, registers, finite state machines), and digital system "
            "design using VHDL or Verilog HDL. Students build circuits on FPGAs in lab. "
            "Foundation for computer architecture, embedded systems, VLSI design, "
            "and FPGA-based computing. "
            "Cross-listed with CS. Useful for anyone interested in hardware or the boundary "
            "between hardware and software."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Calhoun, B."},
        ],
        "difficulty": 3, "workload_hrs_week": 9,
        "tags": ["digital logic","hardware","FPGA","Verilog","VHDL","circuits","embedded systems","computer architecture","Boolean algebra","HDL"],
        "reviews": "Loved building real circuits. FPGA labs are the best part.",
    },
    {
        "id": "ECE4435",
        "mnemonic": "ECE", "number": 4435,
        "title": "Computer Architecture",
        "description": (
            "Design of modern processor architectures: instruction set architectures (x86, RISC-V), "
            "pipelining and hazard handling, memory hierarchy (caches, virtual memory, TLBs), "
            "branch prediction, out-of-order execution, SIMD, and multicore systems. "
            "Students implement a pipelined RISC-V CPU in Verilog. "
            "Deepens understanding of how hardware and software interact. "
            "Critical background for high-performance computing, GPU programming, "
            "and systems software engineering."
        ),
        "credits": 3, "prereqs": ["ECE2330","CS2130"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Stan, M."},
        ],
        "difficulty": 5, "workload_hrs_week": 13,
        "tags": ["computer architecture","RISC-V","pipelining","cache","CPU design","Verilog","hardware","performance","HPC","x86","GPU"],
        "reviews": "Extremely hard but the most I've ever learned in a semester. CPU implementation is brutal.",
    },
    {
        "id": "ECE3750",
        "mnemonic": "ECE", "number": 3750,
        "title": "Signals and Systems",
        "description": (
            "Continuous and discrete-time signal processing. Linear time-invariant systems, "
            "convolution, Fourier series and transforms, Laplace transforms, Z-transforms, "
            "sampling theorem, FIR and IIR filter design. "
            "Applications to audio processing, communications, and control systems. "
            "Students implement filters in MATLAB and Python. "
            "Foundation for wireless communications, audio engineering, radar, biomedical imaging, "
            "and any field involving signal acquisition and processing."
        ),
        "credits": 3, "prereqs": ["MATH3250"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "11:00", "end": "11:50", "instructor": "Acton, S."},
        ],
        "difficulty": 4, "workload_hrs_week": 10,
        "tags": ["signals","systems","Fourier transform","DSP","filtering","MATLAB","audio","communications","control systems","convolution","Laplace"],
        "reviews": "Challenging math but beautiful theory. Great if you like applied math.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "MATH1310",
        "mnemonic": "MATH", "number": 1310,
        "title": "Calculus I",
        "description": (
            "Differential calculus of single-variable functions. Limits and continuity, "
            "the derivative and differentiation rules (product, chain, implicit), "
            "applications of derivatives (related rates, optimization, curve sketching), "
            "and an introduction to the integral via antiderivatives and the Fundamental Theorem. "
            "Required prerequisite for most STEM sequences. "
            "Students who struggled with high school precalculus should consider MATH 1190 first."
        ),
        "credits": 4, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "08:00", "end": "08:50", "instructor": "Thomas, L."},
            {"section": "002", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Staff"},
            {"section": "003", "days": ["Mon","Wed","Fri"], "start": "13:00", "end": "13:50", "instructor": "Staff"},
        ],
        "difficulty": 3, "workload_hrs_week": 8,
        "tags": ["calculus","derivatives","limits","optimization","math","STEM","integrals","Fundamental Theorem"],
        "reviews": "Standard calc course. Go to office hours and you'll be fine.",
    },
    {
        "id": "MATH1320",
        "mnemonic": "MATH", "number": 1320,
        "title": "Calculus II",
        "description": (
            "Techniques of integration (substitution, integration by parts, partial fractions, "
            "trig substitution), improper integrals, infinite series and convergence tests, "
            "power series and Taylor series, parametric equations, and polar coordinates. "
            "Taylor series and approximation are used throughout science and engineering. "
            "More algebraically demanding than Calculus I — students should be comfortable "
            "with derivatives before starting."
        ),
        "credits": 4, "prereqs": ["MATH1310"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "09:00", "end": "09:50", "instructor": "Staff"},
            {"section": "002", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Krishtal, I."},
        ],
        "difficulty": 4, "workload_hrs_week": 9,
        "tags": ["calculus","integration","Taylor series","power series","math","STEM","series convergence","polar coordinates"],
        "reviews": "Much harder than Calc I. Taylor series will haunt you.",
    },
    {
        "id": "MATH2310",
        "mnemonic": "MATH", "number": 2310,
        "title": "Calculus III (Multivariable)",
        "description": (
            "Calculus of functions of several variables. Vectors and the geometry of 3-D space, "
            "partial derivatives, gradient, directional derivatives, multiple integrals, "
            "line and surface integrals, and the theorems of Green, Stokes, and the Divergence theorem. "
            "Essential for physics, engineering, and machine learning (gradients, Jacobians, Hessians). "
            "Builds geometric intuition for higher-dimensional spaces."
        ),
        "credits": 4, "prereqs": ["MATH1320"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Zhu, W."},
        ],
        "difficulty": 3, "workload_hrs_week": 9,
        "tags": ["multivariable calculus","partial derivatives","gradient","multiple integrals","vector calculus","math","STEM","3D geometry","Stokes theorem"],
        "reviews": "Beautiful course. Stokes' theorem blew my mind.",
    },
    {
        "id": "MATH3351",
        "mnemonic": "MATH", "number": 3351,
        "title": "Elementary Linear Algebra",
        "description": (
            "Vectors and vector spaces, matrix operations, systems of linear equations, "
            "determinants, eigenvalues and eigenvectors, diagonalization, inner product spaces, "
            "least squares, and the singular value decomposition (SVD). "
            "Linear algebra is the mathematical backbone of machine learning, computer graphics, "
            "data science, quantum computing, and engineering. "
            "Balances concrete computation with conceptual understanding of linear transformations."
        ),
        "credits": 3, "prereqs": ["MATH1310"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Krainer, T."},
            {"section": "002", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Staff"},
        ],
        "difficulty": 3, "workload_hrs_week": 7,
        "tags": ["linear algebra","matrices","eigenvalues","SVD","vectors","math","machine learning foundation","data science","graphics","least squares","diagonalization"],
        "reviews": "Must-take for anyone going into ML or data science. Elegant material.",
    },
    {
        "id": "MATH3250",
        "mnemonic": "MATH", "number": 3250,
        "title": "Ordinary Differential Equations",
        "description": (
            "First and second order ordinary differential equations (separation of variables, "
            "integrating factors, undetermined coefficients, variation of parameters), "
            "systems of ODEs, phase plane analysis, Laplace transforms, and an introduction "
            "to partial differential equations. "
            "Applications to population dynamics, mechanical vibrations, electrical circuits, "
            "and heat flow. Essential for physics, engineering, and mathematical modeling."
        ),
        "credits": 3, "prereqs": ["MATH1320"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Zhu, W."},
        ],
        "difficulty": 3, "workload_hrs_week": 8,
        "tags": ["differential equations","ODEs","Laplace transform","modeling","math","physics","engineering","dynamical systems","phase plane"],
        "reviews": "Solid applied math. Laplace transforms section was my favorite.",
    },
    {
        "id": "MATH4310",
        "mnemonic": "MATH", "number": 4310,
        "title": "Introduction to Real Analysis",
        "description": (
            "Rigorous treatment of real numbers, sequences and series, limits, continuity, "
            "differentiability, and Riemann integration. Emphasis on epsilon-delta proofs "
            "and developing mathematical maturity. "
            "The hardest undergraduate math course for most students. "
            "Essential for graduate school in mathematics, statistics, economics, or any field "
            "requiring rigorous mathematical reasoning. Changes how you think about calculus "
            "forever."
        ),
        "credits": 3, "prereqs": ["MATH2310","MATH3351"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "13:00", "end": "13:50", "instructor": "Krainer, T."},
        ],
        "difficulty": 5, "workload_hrs_week": 14,
        "tags": ["real analysis","proofs","epsilon-delta","sequences","continuity","rigorous math","grad school prep","analysis"],
        "reviews": "The hardest course I've taken. Only attempt if you genuinely love math.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # STATISTICS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "STAT2120",
        "mnemonic": "STAT", "number": 2120,
        "title": "Introduction to Statistical Analysis",
        "description": (
            "Descriptive statistics, probability, discrete and continuous distributions, "
            "sampling, hypothesis testing (t-tests, chi-square, ANOVA), confidence intervals, "
            "and simple linear regression. Uses JMP and R for data analysis. "
            "Practical, computation-focused introduction for non-math majors. "
            "Good prep for research methods in social sciences, biology, and public health."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Woo, J."},
            {"section": "002", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Staff"},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["statistics","probability","hypothesis testing","regression","R","ANOVA","data analysis","intro","research methods"],
        "reviews": "Solid intro stats. R assignments are useful. Not too theoretical.",
    },
    {
        "id": "STAT3120",
        "mnemonic": "STAT", "number": 3120,
        "title": "Mathematical Statistics",
        "description": (
            "Probability theory and mathematical statistics at the calculus level. "
            "Random variables, probability distributions (binomial, Poisson, normal, exponential), "
            "moment generating functions, the Central Limit Theorem, point and interval estimation, "
            "likelihood and maximum likelihood estimation, and hypothesis testing theory. "
            "Essential for data science, machine learning, and any quantitative research field. "
            "Proof-based with real data examples using R."
        ),
        "credits": 3, "prereqs": ["MATH1320"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "12:00", "end": "12:50", "instructor": "Woo, J."},
        ],
        "difficulty": 4, "workload_hrs_week": 10,
        "tags": ["mathematical statistics","probability","MLE","CLT","distributions","R","data science","hypothesis testing","Bayesian","quantitative research"],
        "reviews": "Rigorous and rewarding. MLE section is beautiful if you like the math.",
    },
    {
        "id": "STAT4630",
        "mnemonic": "STAT", "number": 4630,
        "title": "Statistical Learning",
        "description": (
            "Statistical perspective on machine learning. Linear and logistic regression revisited "
            "rigorously, model selection and regularization (Ridge, LASSO), cross-validation, "
            "splines, GAMs, tree-based methods (CART, random forests, boosting), "
            "support vector machines, and neural networks from a statistical viewpoint. "
            "Uses R with caret and tidymodels. Based on the ISLR textbook. "
            "Bridges statistics and modern ML — complements CS machine learning courses "
            "by emphasizing inference, uncertainty, and model interpretability."
        ),
        "credits": 3, "prereqs": ["STAT3120","MATH3351"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "15:30", "end": "16:45", "instructor": "Dobra, A."},
        ],
        "difficulty": 4, "workload_hrs_week": 11,
        "tags": ["statistical learning","machine learning","LASSO","Ridge","random forests","R","model selection","boosting","SVM","cross-validation","interpretable ML","ISLR"],
        "reviews": "Perfect complement to CS4501-ML. R-based. Focus on understanding, not just accuracy.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # DATA SCIENCE
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "DS1002",
        "mnemonic": "DS", "number": 1002,
        "title": "Programming for Data Science",
        "description": (
            "Practical programming in Python and R for data analysis. Python: pandas for data "
            "manipulation, NumPy for numerical computing, Matplotlib and Seaborn for visualization, "
            "and an introduction to scikit-learn. R: tidyverse, ggplot2, and dplyr. "
            "Students work with real-world datasets (elections, sports, climate, public health). "
            "No prior programming experience needed — this is the entry point for the Data Science major. "
            "Builds immediately marketable skills for research assistantships and data analyst roles."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Alonzi, P."},
            {"section": "002", "days": ["Mon","Wed"], "start": "14:00", "end": "15:15", "instructor": "Gates, A."},
        ],
        "difficulty": 2, "workload_hrs_week": 7,
        "tags": ["data science","python","R","pandas","NumPy","visualization","ggplot2","tidyverse","scikit-learn","beginner","data analysis","matplotlib"],
        "reviews": "Great intro. You'll learn Python and R simultaneously. Projects use real data.",
    },
    {
        "id": "DS3001",
        "mnemonic": "DS", "number": 3001,
        "title": "Foundations of Machine Learning",
        "description": (
            "Applied machine learning using Python's scikit-learn ecosystem. Covers the full ML "
            "pipeline: data cleaning, exploratory analysis, feature engineering, model training, "
            "hyperparameter tuning, cross-validation, and evaluation metrics. "
            "Algorithms: k-NN, linear models, SVMs, decision trees, random forests, and gradient "
            "boosting (XGBoost). "
            "Final project uses a real-world dataset from a domain of the student's choosing "
            "(healthcare, finance, sports, social media). "
            "More applied and less theoretical than CS4501-ML — excellent for students who want "
            "ML skills for data science without diving deep into math."
        ),
        "credits": 3, "prereqs": ["DS1002","STAT2120"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "09:00", "end": "10:15", "instructor": "Lorenz, B."},
        ],
        "difficulty": 3, "workload_hrs_week": 9,
        "tags": ["machine learning","scikit-learn","data science","XGBoost","feature engineering","python","applied ML","random forests","gradient boosting","evaluation","pipelines"],
        "reviews": "Best practical ML course for data science students. Real datasets make it interesting.",
    },
    {
        "id": "DS4002",
        "mnemonic": "DS", "number": 4002,
        "title": "Data Science Project",
        "description": (
            "Capstone project course for Data Science majors. Teams of 3–4 students identify a "
            "real-world problem, collect or source data, apply appropriate ML and statistical "
            "techniques, and present findings to an audience including industry partners. "
            "Past projects have included predicting hospital readmission, modeling Charlottesville "
            "traffic, analyzing UVA athletics performance, and building NLP tools for legal documents. "
            "Students develop data storytelling and communication skills alongside technical work. "
            "Faculty and industry mentors provide guidance throughout."
        ),
        "credits": 3, "prereqs": ["DS3001"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Alonzi, P."},
        ],
        "difficulty": 3, "workload_hrs_week": 12,
        "tags": ["data science","capstone","project","machine learning","data storytelling","communication","team project","applied","real-world","consulting"],
        "reviews": "Loved working on a real project with industry feedback. Portfolio gold.",
    },
    {
        "id": "DS5559",
        "mnemonic": "DS", "number": 5559,
        "title": "Big Data Systems",
        "description": (
            "Distributed computing and data engineering at scale. MapReduce and Apache Spark, "
            "data warehousing with Snowflake and BigQuery, stream processing with Kafka, "
            "data pipeline orchestration with Airflow, and cloud infrastructure on AWS and GCP. "
            "Students build a complete ETL pipeline and analytical dashboard for a large dataset. "
            "Directly relevant to data engineering, MLOps, and analytics engineering roles at "
            "tech companies, financial firms, and healthcare organizations."
        ),
        "credits": 3, "prereqs": ["CS4750","DS3001"],
        "sections": [
            {"section": "001", "days": ["Wed"], "start": "18:00", "end": "20:30", "instructor": "Brown, R."},
        ],
        "difficulty": 4, "workload_hrs_week": 13,
        "tags": ["big data","Spark","Kafka","AWS","data engineering","MLOps","ETL","cloud","Airflow","Snowflake","distributed computing","data pipelines"],
        "reviews": "Very industry-relevant. Spark assignments are hard but rewarding.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ECONOMICS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "ECON2010",
        "mnemonic": "ECON", "number": 2010,
        "title": "Principles of Microeconomics",
        "description": (
            "Supply and demand, consumer choice theory, production and costs, market structures "
            "(perfect competition, monopoly, oligopoly), game theory basics, externalities, "
            "public goods, and information asymmetries. "
            "Foundational for economics, business, public policy, and law. "
            "Uses graphical and algebraic analysis — no calculus required. "
            "Helps students think rigorously about incentives, trade-offs, and market design."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Pepper, J."},
            {"section": "002", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Staff"},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["microeconomics","supply and demand","game theory","market structure","economics","business","policy","incentives","consumer theory"],
        "reviews": "Pepper is fantastic. Makes econ intuitive and interesting.",
    },
    {
        "id": "ECON2020",
        "mnemonic": "ECON", "number": 2020,
        "title": "Principles of Macroeconomics",
        "description": (
            "National income accounting, GDP, unemployment and inflation, the business cycle, "
            "fiscal policy (government spending and taxes), monetary policy (Federal Reserve, "
            "interest rates), international trade and exchange rates, and economic growth theory. "
            "Contextualizes current events — students learn to read the Wall Street Journal "
            "with economic understanding. Accessible to non-economists."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "11:00", "end": "11:50", "instructor": "Staff"},
        ],
        "difficulty": 2, "workload_hrs_week": 5,
        "tags": ["macroeconomics","GDP","monetary policy","Federal Reserve","fiscal policy","inflation","trade","economics","current events","policy"],
        "reviews": "Easy A if you follow the news. Great survey of macro concepts.",
    },
    {
        "id": "ECON3720",
        "mnemonic": "ECON", "number": 3720,
        "title": "Introduction to Econometrics",
        "description": (
            "Statistical methods for empirical economic research. OLS regression (assumptions, "
            "interpretation, violations), heteroscedasticity, serial correlation, instrumental "
            "variables and two-stage least squares, panel data methods (fixed effects, "
            "random effects), differences-in-differences, regression discontinuity, and "
            "an introduction to causal inference. Students use R or Stata on real economic datasets. "
            "Essential for any student planning empirical research in economics, finance, "
            "or public policy. Increasingly valued in data science roles too."
        ),
        "credits": 3, "prereqs": ["ECON2010","STAT2120"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Nguyen, T."},
        ],
        "difficulty": 4, "workload_hrs_week": 10,
        "tags": ["econometrics","causal inference","regression","OLS","panel data","R","Stata","empirical research","difference-in-differences","instrumental variables","economics","quantitative"],
        "reviews": "Best applied stats course at UVA if you want to do real empirical work.",
    },
    {
        "id": "ECON4080",
        "mnemonic": "ECON", "number": 4080,
        "title": "Labor Economics",
        "description": (
            "Economic analysis of labor markets: labor supply and demand, human capital theory, "
            "wage determination, discrimination, unions, unemployment, immigration, and "
            "the impact of technology on employment. Extensive use of empirical studies. "
            "Highly relevant to public policy debates about minimum wages, education returns, "
            "and automation. "
            "Good complement to econometrics for students interested in applied micro research."
        ),
        "credits": 3, "prereqs": ["ECON2010","ECON3720"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "14:00", "end": "15:15", "instructor": "Turner, S."},
        ],
        "difficulty": 3, "workload_hrs_week": 8,
        "tags": ["labor economics","wages","human capital","discrimination","unemployment","policy","empirical economics","applied micro","automation","inequality"],
        "reviews": "Turner is one of the best professors at UVA. Very policy-relevant.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # BIOLOGY
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "BIOL2100",
        "mnemonic": "BIOL", "number": 2100,
        "title": "Cell Biology and Genetics",
        "description": (
            "Molecular biology of the cell: DNA replication, transcription, translation, "
            "gene regulation, signal transduction, cell division (mitosis and meiosis), "
            "and the principles of Mendelian and molecular genetics. "
            "Lab component includes PCR, gel electrophoresis, and microscopy. "
            "Gateway course for biology, neuroscience, and pre-med students. "
            "Rigorous and content-heavy — students should expect significant memorization "
            "alongside conceptual understanding."
        ),
        "credits": 4, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Kozminski, K."},
        ],
        "difficulty": 3, "workload_hrs_week": 10,
        "tags": ["biology","cell biology","genetics","DNA","pre-med","molecular biology","PCR","lab","neuroscience","MCAT"],
        "reviews": "Dense material but excellent instructors. Lab section is genuinely fun.",
    },
    {
        "id": "BIOL3250",
        "mnemonic": "BIOL", "number": 3250,
        "title": "Neuroscience: Brain and Behavior",
        "description": (
            "Introduction to neuroscience covering neural signaling (action potentials, synaptic "
            "transmission), sensory systems (vision, audition, touch), motor control, learning "
            "and memory (LTP, hippocampus), sleep, reward and addiction, and psychiatric disorders. "
            "Connects cellular neuroscience to behavior and psychological phenomena. "
            "Ideal for students interested in the brain, mental health, psychology, or "
            "building brain-computer interfaces and neuromorphic computing systems."
        ),
        "credits": 3, "prereqs": ["BIOL2100"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Bhatt, D."},
        ],
        "difficulty": 3, "workload_hrs_week": 9,
        "tags": ["neuroscience","brain","behavior","neurons","memory","learning","mental health","addiction","pre-med","psychology","brain-computer interface"],
        "reviews": "Fascinating — the sleep and memory sections are especially engaging.",
    },
    {
        "id": "BIOL4559",
        "mnemonic": "BIOL", "number": 4559,
        "title": "Bioinformatics",
        "description": (
            "Computational methods for analyzing biological data. Sequence alignment (BLAST, "
            "dynamic programming), genome assembly, phylogenetic analysis, protein structure "
            "prediction, gene expression analysis with RNA-seq, and machine learning applications "
            "in genomics. Python and R used throughout. "
            "At the intersection of computer science, statistics, and biology. "
            "Ideal for students interested in computational biology, personalized medicine, "
            "biotech, or academic research."
        ),
        "credits": 3, "prereqs": ["BIOL2100","CS1110"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "11:00", "end": "12:15", "instructor": "Pearson, W."},
        ],
        "difficulty": 4, "workload_hrs_week": 11,
        "tags": ["bioinformatics","computational biology","genomics","RNA-seq","sequence alignment","BLAST","python","R","machine learning","biotech","personalized medicine","research"],
        "reviews": "Perfect mix of bio and CS. Protein structure prediction section was mind-blowing.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # CHEMISTRY
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "CHEM1410",
        "mnemonic": "CHEM", "number": 1410,
        "title": "Introductory Chemistry I",
        "description": (
            "Atomic structure, periodic trends, chemical bonding (ionic, covalent, metallic), "
            "molecular geometry (VSEPR), stoichiometry, solution chemistry, and gas laws. "
            "Laboratory component includes quantitative analysis and synthesis. "
            "Required for pre-med, nursing, and most natural science majors. "
            "Assumes high school chemistry background — students without it should consider CHEM 1010."
        ),
        "credits": 4, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "09:00", "end": "09:50", "instructor": "Grisham, C."},
        ],
        "difficulty": 3, "workload_hrs_week": 10,
        "tags": ["chemistry","atoms","bonding","stoichiometry","lab","pre-med","general chemistry","molecular geometry"],
        "reviews": "Dense but well-organized. Labs are well-designed.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PHYSICS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PHYS1425",
        "mnemonic": "PHYS", "number": 1425,
        "title": "Physics I: Mechanics",
        "description": (
            "Calculus-based classical mechanics. Kinematics, Newton's laws, work-energy theorem, "
            "conservation of momentum, rotational motion (torque, angular momentum), simple harmonic "
            "motion, and universal gravitation. Weekly lab section. "
            "Required for engineering, physics, and most natural science programs. "
            "Combines mathematical rigor with physical intuition. "
            "Students who found high school physics algebra-based will find this a step up."
        ),
        "credits": 4, "prereqs": ["MATH1310"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "09:00", "end": "09:50", "instructor": "Kos, S."},
        ],
        "difficulty": 3, "workload_hrs_week": 10,
        "tags": ["physics","mechanics","Newton's laws","energy","momentum","rotation","calculus-based","lab","engineering","STEM"],
        "reviews": "Well-taught. Lab section reinforces lectures nicely.",
    },
    {
        "id": "PHYS1710",
        "mnemonic": "PHYS", "number": 1710,
        "title": "Physics II: Electricity and Magnetism",
        "description": (
            "Electric fields and potentials, Gauss's law, capacitors and dielectrics, DC and AC circuits, "
            "magnetic fields, Faraday's law, and Maxwell's equations. "
            "Foundation for electronics, wireless communications, and photonics. "
            "Math-intensive — multivariable calculus is used extensively. "
            "Lab component includes oscilloscopes, circuit building, and optics experiments."
        ),
        "credits": 4, "prereqs": ["PHYS1425","MATH2310"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Hirosky, R."},
        ],
        "difficulty": 4, "workload_hrs_week": 11,
        "tags": ["physics","electricity","magnetism","Maxwell's equations","circuits","E&M","calculus-based","lab","electronics","engineering"],
        "reviews": "Hardest intro physics course. Maxwell's equations are beautiful but the math is intense.",
    },
    {
        "id": "PHYS3650",
        "mnemonic": "PHYS", "number": 3650,
        "title": "Quantum Mechanics I",
        "description": (
            "Wave-particle duality, the Schrödinger equation, quantum states, operators and observables, "
            "the uncertainty principle, quantum wells, harmonic oscillator, hydrogen atom, and "
            "introduction to spin. "
            "The strangest and most beautiful theory in physics. "
            "Essential for modern chemistry, materials science, quantum computing, and "
            "semiconductor device physics. "
            "Demands strong calculus and differential equations background."
        ),
        "credits": 3, "prereqs": ["PHYS1710","MATH3250"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Smirl, A."},
        ],
        "difficulty": 5, "workload_hrs_week": 13,
        "tags": ["quantum mechanics","quantum computing","physics","Schrödinger equation","wave function","uncertainty principle","materials science","semiconductor","chemistry"],
        "reviews": "Mind-bending. One of the most intellectually stimulating courses at UVA.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PHILOSOPHY / ETHICS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PHIL1500",
        "mnemonic": "PHIL", "number": 1500,
        "title": "Introduction to Philosophy",
        "description": (
            "Survey of major philosophical questions and traditions. Metaphysics (the nature of "
            "reality, free will, personal identity), epistemology (knowledge and skepticism), "
            "ethics (what is morally right), and political philosophy (justice, rights, democracy). "
            "Readings from Plato, Descartes, Hume, Kant, Mill, and contemporary philosophers. "
            "Discussion-based and writing-intensive. Develops critical thinking and argumentation "
            "skills valued in law, medicine, policy, and leadership."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Kumar, V."},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["philosophy","ethics","critical thinking","metaphysics","logic","epistemology","humanities","writing","law school prep","argumentation"],
        "reviews": "Fantastic for sharpening your thinking. Great writing feedback.",
    },
    {
        "id": "PHIL2160",
        "mnemonic": "PHIL", "number": 2160,
        "title": "Ethics of Emerging Technologies",
        "description": (
            "Philosophical and ethical analysis of artificial intelligence, autonomous systems, "
            "social media algorithms, genetic editing, surveillance capitalism, and data privacy. "
            "Frameworks applied: consequentialism, deontology, virtue ethics, and care ethics. "
            "Students read primary philosophy alongside tech policy papers, journalism, and "
            "company ethics guidelines. Weekly case studies include self-driving car trolley "
            "problems, facial recognition in policing, and AI-generated misinformation. "
            "No technical background required. Cross-listed with STS."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "11:00", "end": "12:15", "instructor": "Wester, M."},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["ethics","AI ethics","technology","privacy","surveillance","philosophy","autonomous vehicles","facial recognition","policy","social media","humanities","responsible AI"],
        "reviews": "Should be required for CS majors. Eye-opening readings and great discussions.",
    },
    {
        "id": "PHIL3210",
        "mnemonic": "PHIL", "number": 3210,
        "title": "Philosophy of Mind and Artificial Intelligence",
        "description": (
            "Can machines think? What is consciousness? This course examines the Turing test, "
            "the Chinese Room argument, functionalism, computational theories of mind, "
            "the hard problem of consciousness, and ethical implications of artificial general "
            "intelligence. Readings from Turing, Searle, Dennett, Chalmers, and Bostrom. "
            "No AI or CS background required — but CS students will find rich connections to "
            "their technical work. Regularly brings in AI researchers as guest speakers."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "13:00", "end": "13:50", "instructor": "Wester, M."},
        ],
        "difficulty": 3, "workload_hrs_week": 7,
        "tags": ["philosophy of mind","artificial intelligence","consciousness","Turing test","AGI","ethics","cognitive science","humanities","interdisciplinary"],
        "reviews": "Thought-provoking like no other. The Chinese Room debate is unforgettable.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PSYCHOLOGY
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PSYC2200",
        "mnemonic": "PSYC", "number": 2200,
        "title": "Cognitive Psychology",
        "description": (
            "Scientific study of mental processes: perception, attention, working memory, "
            "long-term memory, mental imagery, language comprehension and production, "
            "problem solving, judgment, and decision making. "
            "Classic experiments (Stroop, change blindness, dual-task) discussed alongside "
            "modern cognitive neuroscience findings. "
            "Relevant to UX design, human-computer interaction, AI (cognitive architectures), "
            "and clinical psychology. "
            "In-class demonstrations make abstract concepts concrete."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "14:00", "end": "14:50", "instructor": "Dennis, N."},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["psychology","cognition","memory","attention","decision making","HCI","UX","neuroscience","perception","behavioral science"],
        "reviews": "Engaging and accessible. Memory section was fascinating.",
    },
    {
        "id": "PSYC3005",
        "mnemonic": "PSYC", "number": 3005,
        "title": "Research Methods in Psychology",
        "description": (
            "Design and analysis of psychological research. Experimental design, sampling, "
            "operationalization of variables, within- and between-subjects designs, surveys, "
            "observational methods, and replication. Statistical analysis in SPSS and R. "
            "APA writing style and ethical standards in human subjects research. "
            "Students design and run a small experiment. Essential for any student planning "
            "to pursue graduate school in psychology or behavioral science."
        ),
        "credits": 3, "prereqs": ["STAT2120"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "15:30", "end": "16:45", "instructor": "Gilbert, D."},
        ],
        "difficulty": 3, "workload_hrs_week": 9,
        "tags": ["research methods","psychology","statistics","experimental design","R","SPSS","behavioral science","grad school prep","APA","human subjects"],
        "reviews": "Teaches you how to actually do science. Valuable for any field.",
    },
    {
        "id": "PSYC4310",
        "mnemonic": "PSYC", "number": 4310,
        "title": "Social Psychology",
        "description": (
            "How people think, feel, and behave in social contexts. Attitude formation and change, "
            "persuasion, conformity and obedience (Milgram), group dynamics, prejudice and "
            "stereotyping, social identity theory, helping behavior, and interpersonal attraction. "
            "Connects classic social psychology to modern social media and political polarization. "
            "Discussion-heavy with regular analysis of current events."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "11:00", "end": "12:15", "instructor": "Haidt, J."},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["social psychology","behavior","persuasion","conformity","prejudice","group dynamics","social media","polarization","humanities","communication"],
        "reviews": "One of the most engaging courses at UVA. Real-world examples are excellent.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ENGLISH / WRITING
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "ENWR1510",
        "mnemonic": "ENWR", "number": 1510,
        "title": "Writing and Critical Inquiry",
        "description": (
            "Foundation writing course required for most College of Arts & Sciences students. "
            "Develops skills in academic argument, evidence evaluation, paragraph structure, "
            "thesis development, and revision. Each section focuses on a different theme — "
            "past themes include surveillance and privacy, food systems, sports and identity, "
            "and science communication. "
            "Heavy revision emphasis: students rewrite every paper at least once. "
            "Small sections (15 students max) ensure substantial instructor feedback."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "11:00", "end": "11:50", "instructor": "Garber, D."},
            {"section": "002", "days": ["Tue","Thu"], "start": "12:30", "end": "13:45", "instructor": "Staff"},
        ],
        "difficulty": 2, "workload_hrs_week": 7,
        "tags": ["writing","academic writing","argument","revision","communication","English","requirement","humanities","critical thinking","essays"],
        "reviews": "Actually improved my writing. Small class means real feedback.",
    },
    {
        "id": "ENWR3800",
        "mnemonic": "ENWR", "number": 3800,
        "title": "Technical and Scientific Writing",
        "description": (
            "Writing in professional and technical contexts: research reports, executive summaries, "
            "grant proposals, user manuals, data visualization and interpretation, and science "
            "communication for general audiences. Students work with their own disciplinary material. "
            "Highly practical — students in engineering, CS, and science fields frequently "
            "cite this as one of their most career-relevant electives. "
            "Includes a section on writing for the web and communicating data visually."
        ),
        "credits": 3, "prereqs": ["ENWR1510"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Pullman, G."},
        ],
        "difficulty": 2, "workload_hrs_week": 7,
        "tags": ["technical writing","science communication","professional writing","reports","grant writing","communication","STEM","data visualization","career skills"],
        "reviews": "Best writing course for STEM students. I use these skills every day at my job.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HISTORY
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "HIST2001",
        "mnemonic": "HIST", "number": 2001,
        "title": "History of Science and Technology",
        "description": (
            "How science and technology have developed from antiquity to the digital age. "
            "The scientific revolution, Industrial Revolution, the atomic bomb, the space race, "
            "the personal computer, the internet, and genomics. "
            "Examines how social, political, and economic forces shape scientific discovery. "
            "Accessible to all majors — no science background required. "
            "CS and engineering students gain historical perspective on their own disciplines."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "13:00", "end": "13:50", "instructor": "Misa, T."},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["history","technology","science","internet","computers","Industrial Revolution","humanities","social context","interdisciplinary"],
        "reviews": "Great context for CS students. Makes you think about the social impact of tech.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # COMMERCE / BUSINESS (McIntire School)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "COMM3010",
        "mnemonic": "COMM", "number": 3010,
        "title": "Financial Accounting",
        "description": (
            "Fundamentals of financial reporting: the accounting cycle, journal entries, trial balance, "
            "income statement, balance sheet, statement of cash flows, accounts receivable, "
            "inventory valuation, depreciation, and basic ratio analysis. "
            "Students analyze real 10-K filings from public companies. "
            "Essential foundation for finance, investment banking, consulting, and entrepreneurship. "
            "Case-based teaching with emphasis on interpreting numbers, not just recording them."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "08:00", "end": "09:15", "instructor": "Brown, T."},
        ],
        "difficulty": 3, "workload_hrs_week": 8,
        "tags": ["accounting","finance","financial statements","balance sheet","business","consulting","investment banking","10-K","entrepreneurship"],
        "reviews": "Tough but essential for finance and consulting recruiting.",
    },
    {
        "id": "COMM4550",
        "mnemonic": "COMM", "number": 4550,
        "title": "Technology Entrepreneurship",
        "description": (
            "Lean startup methodology, customer discovery interviews, product-market fit, "
            "venture capital fundraising, cap tables, pitch decks, go-to-market strategy, "
            "and scaling a tech startup. Guest speakers include UVA-connected founders (WillowTree, "
            "Cvillian ventures). Students develop and pitch their own startup ideas to a panel "
            "of investors. "
            "Best entrepreneurship course at UVA for students building tech companies. "
            "Partners with UVA's iLab incubator."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "15:30", "end": "16:45", "instructor": "Weiss, J."},
        ],
        "difficulty": 2, "workload_hrs_week": 8,
        "tags": ["entrepreneurship","startups","venture capital","product","business","pitch","lean startup","tech company","founders","iLab","fundraising"],
        "reviews": "Incredible energy. Real investor feedback on your pitch is invaluable.",
    },
    {
        "id": "COMM4559",
        "mnemonic": "COMM", "number": 4559,
        "title": "Business Analytics",
        "description": (
            "Data-driven decision making in business contexts. Descriptive analytics (dashboards, "
            "KPIs), predictive modeling (regression, classification), prescriptive analytics "
            "(optimization, simulation), and A/B testing. Tools: Excel, Tableau, and Python. "
            "Students work on real business cases in teams. "
            "Ideal for students who want to work in analytics, product management, strategy "
            "consulting, or operations at technology and consumer companies."
        ),
        "credits": 3, "prereqs": ["STAT2120"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "15:30", "end": "16:45", "instructor": "Jones, A."},
        ],
        "difficulty": 3, "workload_hrs_week": 9,
        "tags": ["business analytics","Tableau","data","A/B testing","product management","strategy","consulting","python","Excel","KPIs","decision making","operations"],
        "reviews": "Very applied. Tableau section is immediately useful at any business internship.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ENVIRONMENTAL SCIENCE
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "EVSC1300",
        "mnemonic": "EVSC", "number": 1300,
        "title": "Introduction to Environmental Sciences",
        "description": (
            "Earth's systems: atmosphere, hydrosphere, lithosphere, and biosphere. "
            "Climate change science (greenhouse effect, feedback loops, tipping points), "
            "biodiversity and ecosystem services, pollution, energy systems, "
            "and sustainability. "
            "Balances scientific rigor with policy context. "
            "Great for students who want to understand climate science quantitatively "
            "without majoring in environmental science. No science background required."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "11:00", "end": "11:50", "instructor": "Porter, J."},
        ],
        "difficulty": 2, "workload_hrs_week": 6,
        "tags": ["environment","climate change","sustainability","ecology","energy","policy","earth science","greenhouse effect","biodiversity"],
        "reviews": "Eye-opening. I now understand climate science beyond the headlines.",
    },
    {
        "id": "EVSC4559",
        "mnemonic": "EVSC", "number": 4559,
        "title": "Climate Data Analysis",
        "description": (
            "Quantitative analysis of climate and environmental data using Python. "
            "Time series analysis, spatial data with GeoPandas, satellite data processing "
            "(NASA MODIS, Landsat), climate model output analysis (CMIP6), "
            "and machine learning for environmental applications. "
            "Students work with real NOAA and NASA datasets. "
            "Ideal for students combining data science skills with environmental interests. "
            "Cross-listed with DS and STAT."
        ),
        "credits": 3, "prereqs": ["DS1002","EVSC1300"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "14:00", "end": "15:15", "instructor": "Ziegler, A."},
        ],
        "difficulty": 3, "workload_hrs_week": 10,
        "tags": ["climate data","Python","satellite data","machine learning","environment","data science","time series","geospatial","NASA","NOAA","sustainability","environmental analytics"],
        "reviews": "Unique course combining data science with climate science. Very rewarding.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SOCIOLOGY
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "SOC1010",
        "mnemonic": "SOC", "number": 1010,
        "title": "Introduction to Sociology",
        "description": (
            "Sociological perspectives on society, culture, social structure, stratification, "
            "race and ethnicity, gender, family, education, religion, and social change. "
            "Classic theorists (Marx, Weber, Durkheim) and contemporary issues. "
            "Develops ability to see personal experience in social context — the 'sociological imagination.' "
            "Good complement for students in public policy, education, public health, or anyone "
            "wanting to understand social inequality."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Mon","Wed","Fri"], "start": "10:00", "end": "10:50", "instructor": "Corse, S."},
        ],
        "difficulty": 2, "workload_hrs_week": 5,
        "tags": ["sociology","society","inequality","race","gender","culture","social change","humanities","policy","public health"],
        "reviews": "Changes how you see the world. Very accessible.",
    },
    {
        "id": "SOC4559",
        "mnemonic": "SOC", "number": 4559,
        "title": "Computational Social Science",
        "description": (
            "Using computational methods to study social phenomena. Web scraping and APIs "
            "(Twitter/X, Reddit), text analysis (sentiment, topic modeling with LDA), "
            "network analysis (social networks with NetworkX), and agent-based modeling. "
            "Python throughout. Students examine real social questions: political polarization, "
            "misinformation spread, community formation online, and labor market discrimination. "
            "Cross-listed with DS and CS. "
            "Excellent for students who want to combine social science interests with programming."
        ),
        "credits": 3, "prereqs": ["SOC1010","DS1002"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "14:00", "end": "15:15", "instructor": "Bail, C."},
        ],
        "difficulty": 3, "workload_hrs_week": 10,
        "tags": ["computational social science","NLP","topic modeling","social networks","text analysis","python","Twitter","polarization","misinformation","network analysis","social media","web scraping"],
        "reviews": "Perfect if you love social science but also want to code. Very cool projects.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SYSTEMS ENGINEERING / OPERATIONS RESEARCH
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "SYS3023",
        "mnemonic": "SYS", "number": 3023,
        "title": "Probability and Statistics for Engineers",
        "description": (
            "Applied probability and statistics for engineering applications. Discrete and continuous "
            "random variables, joint distributions, reliability analysis, estimation, confidence "
            "intervals, hypothesis testing, and regression. "
            "Uses Python and MATLAB for simulation and analysis. "
            "More applied than MATH3120 — emphasizes engineering judgment and interpretation "
            "alongside statistical rigor. Required for Systems and Industrial Engineering majors."
        ),
        "credits": 3, "prereqs": ["MATH1320"],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "09:30", "end": "10:45", "instructor": "Dugas, M."},
        ],
        "difficulty": 3, "workload_hrs_week": 8,
        "tags": ["probability","statistics","engineering","reliability","simulation","python","MATLAB","distributions","regression","systems engineering"],
        "reviews": "Well-structured and applied. Good balance of theory and practice.",
    },
    {
        "id": "SYS4582",
        "mnemonic": "SYS", "number": 4582,
        "title": "Reinforcement Learning",
        "description": (
            "Markov decision processes (MDPs), dynamic programming (policy and value iteration), "
            "Monte Carlo methods, temporal-difference learning (Q-learning, SARSA), function "
            "approximation, deep Q-networks (DQN), policy gradient methods (REINFORCE, PPO), "
            "and multi-agent reinforcement learning. "
            "Students implement RL agents in OpenAI Gym and train them on classic control "
            "and Atari game environments. "
            "Directly relevant to robotics, autonomous systems, game AI, and optimizing "
            "recommendation systems. Cross-listed with CS and ECE."
        ),
        "credits": 3, "prereqs": ["CS4501-ML","STAT3120"],
        "sections": [
            {"section": "001", "days": ["Mon","Wed"], "start": "15:30", "end": "16:45", "instructor": "Behl, M."},
        ],
        "difficulty": 5, "workload_hrs_week": 13,
        "tags": ["reinforcement learning","RL","deep learning","robotics","autonomous systems","DQN","policy gradient","game AI","OpenAI Gym","Atari","MDPs","recommendation systems"],
        "reviews": "Hardest elective I've taken. Absolutely worth it if you're into AI research.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PUBLIC POLICY
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "PPL3050",
        "mnemonic": "PPL", "number": 3050,
        "title": "Technology Policy",
        "description": (
            "Policy issues surrounding emerging technologies: AI regulation, data privacy laws "
            "(GDPR, CCPA), antitrust and big tech, platform content moderation, cybersecurity "
            "policy, and the governance of autonomous vehicles and biotechnology. "
            "Students analyze real policy cases and draft their own policy memos. "
            "Guest speakers include government officials, lobbyists, and tech company policy teams. "
            "No technical or policy background required. "
            "Strong preparation for careers in government, think tanks, or tech policy roles."
        ),
        "credits": 3, "prereqs": [],
        "sections": [
            {"section": "001", "days": ["Tue","Thu"], "start": "15:30", "end": "16:45", "instructor": "Rotenberg, M."},
        ],
        "difficulty": 2, "workload_hrs_week": 7,
        "tags": ["technology policy","AI regulation","privacy","GDPR","antitrust","big tech","content moderation","cybersecurity policy","government","law","ethics","autonomous vehicles"],
        "reviews": "Eye-opening for CS students who don't think about regulation. Very topical.",
    },
]

# ── Student profiles for demo / testing ────────────────────────────────────────
EXAMPLE_PROFILES = [
    {
        "name": "Alex — CS Junior",
        "major": "Computer Science",
        "year": 3,
        "completed": ["CS1110","CS2100","CS2120","CS2130","MATH1310","MATH1320","MATH3351","ENWR1510"],
        "busy_times": [],
    },
    {
        "name": "Jordan — Data Science Sophomore",
        "major": "Data Science",
        "year": 2,
        "completed": ["DS1002","MATH1310","STAT2120","ENWR1510"],
        "busy_times": [{"days":["Mon","Wed"],"start":"08:00","end":"09:30"}],
    },
    {
        "name": "Sam — Undeclared Freshman",
        "major": "Undeclared",
        "year": 1,
        "completed": [],
        "busy_times": [{"days":["Tue","Thu"],"start":"09:00","end":"11:00"}],
    },
    {
        "name": "Riley — Pre-med Sophomore",
        "major": "Biology",
        "year": 2,
        "completed": ["BIOL2100","CHEM1410","MATH1310","ENWR1510","PSYC2200"],
        "busy_times": [{"days":["Mon","Wed","Fri"],"start":"15:00","end":"17:00"}],
    },
]
