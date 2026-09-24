# Topic backlog

Posts are written top-down. Add, remove or reorder freely.

## LLMs, RAG and agents
- [ ] Build a RAG pipeline from scratch in ~100 lines of Python (local embeddings, no API key)
- [ ] Make an LLM cite its sources or say "I don't know": grounded answers with a retrieval-miss fallback
- [ ] Chunking strategies for RAG compared on the same documents: fixed, recursive, by heading
- [ ] Write a tool-calling agent loop from scratch that actually stops
- [ ] Text-to-SQL with a small local model and a SQLite guard against destructive queries
- [ ] Redact PII before sending text to an LLM, then restore it in the reply
- [ ] LLM-as-judge: score chatbot answers with pass/fail criteria you can unit-test
- [ ] Route prompts between a cheap and an expensive LLM with a simple classifier
- [ ] Speech-to-text with Whisper, then summarize the transcript locally
- [ ] Fine-tune a small language model with LoRA on a CPU-sized dataset

## Computer vision
- [ ] Object detection on a video file with YOLO in 30 lines
- [ ] Count people crossing a line in a video with YOLO + tracking
- [ ] Train a custom YOLO model on a tiny public dataset
- [ ] Action recognition on short clips: from frames to a classifier
- [ ] Image data augmentation that doesn't break your labels

## Medical imaging
- [ ] U-Net segmentation from scratch on a public medical dataset, measured with Dice and IoU
- [ ] Why accuracy lies in medical imaging: Dice, IoU and class imbalance with real numbers

## Machine learning fundamentals
- [ ] Linear regression, then gradient descent, from scratch in NumPy
- [ ] Decision tree from scratch, checked against scikit-learn
- [ ] Handling imbalanced data: undersampling with a Gaussian Mixture Model
- [ ] Hyperparameter search that doesn't overfit: nested CV explained with code
- [ ] Evolve a neural network's weights with a genetic algorithm

## Time series and trading
- [ ] Stock price prediction without look-ahead leakage: a walk-forward backtest
- [ ] Feature engineering for time series that doesn't leak the future

## Reinforcement learning
- [ ] Q-learning from scratch on a grid world, with a plot of the learning curve
- [ ] Train a CartPole agent with DQN in PyTorch

## Python and web
- [ ] Serve an ML model with FastAPI: validation, batching and a health check
- [ ] Django + a background ML job: upload an image, get a prediction
- [ ] Feature flags for AI features with OpenFeature
- [ ] Python interview questions that actually test understanding, with code
