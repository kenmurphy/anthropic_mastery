# Anthropic Mastery Project Brief

## Project Overview
We're building an AI conversation analysis and learning platform that addresses the challenge of users becoming dependent on AI assistance without building domain expertise. The system analyzes conversation patterns from AI interactions to create structured learning experiences that build long-term mastery.

## Core Concept
The Anthropic Economic Index shows that 57% of AI interactions are augmentative (collaborative human-AI work) rather than fully automated. With these augmentative tasks, users often lean too heavily on AI for basic tasks with minimal engagement with underlying concepts. Users achieve immediate results but miss opportunities to build domain mastery and become less productive long-term.

Our solution creates a structured review layer on top of user prompt history, providing dedicated learning sessions based on conversation history from the past week. This timing is deliberate: recent enough that concepts remain relevant to current work, but separated enough to allow for reflection and deeper understanding.

## Primary Goals

### 1. **Conversation Intelligence & Pattern Recognition**
- AI-Inferred Project Clustering: Automatically groups conversations from the past week into thematic projects
- Repetition Detection: Identifies when users ask similar questions multiple times (e.g., repeated SQL join queries, similar debugging patterns)
- Dependency Mapping: Tracks which foundational concepts users consistently delegate to AI rather than learning

### 2. **Proficiency Assessment Framework**
- Three-Tier System: Beginner, Intermediate, Advanced classifications per concept
- Contextual Adjacency: Identifies related concepts at similar difficulty levels
- Progressive Complexity: Maps user's current understanding against the full learning trajectory

### 3. **Adaptive Learning Interventions**
- Weekly Learning Summaries: Automated reports showing concepts repeatedly queried, current proficiency levels, and suggested learning focus areas
- Learning Modules: 5-10 minute focused sessions on specific concepts
- Interactive quizzes on frequently delegated tasks
- Practice problems that gradually reduce AI assistance

## Target Occupational Tasks

### Primary Focus (37.2% of queries) - Computer & Mathematical Tasks:
- Software modification and architecture decisions
- Code debugging and error resolution
- Network troubleshooting and system design
- Algorithm implementation and optimization
- Database query construction and optimization

### Secondary Focus (10.3% of queries) - Content Creation & Communication Tasks:
- Technical writing and documentation
- Content editing and refinement
- Strategic communication and messaging
- Creative ideation and narrative structure
- Style consistency and tone adaptation

## Key Features & User Journey

### Page 1: Conversations (Data Seeding)
Basic clone of Claude conversations page to seed conversation data for analysis.

### Page 2: Claude Mastery Homepage
- Visualization of user's knowledge map
- Interactive exploration of knowledge areas
- Entry points to dive into specific concepts for mastery

### Page 3: Knowledge Overview
- Study guide of topics user has been covering
- Related topics and learning pathways
- Proficiency tracking and progress visualization

### Page 4: Flashcards
- AI-generated flashcards based on conversation patterns
- Spaced repetition system for knowledge retention
- Focus on frequently delegated concepts

### Page 5: Feynman Technique
- Interactive explanation sessions where users teach back concepts
- Real-time AI feedback on explanations
- Progressive complexity in explanation requirements

## Integration with Bloom's Taxonomy

The learning system scaffolds from lower to higher cognitive functions:
- **Remember**: Quick recall quizzes on syntax and terminology
- **Understand**: Conceptual explanations of underlying principles
- **Apply**: Guided practice with decreasing AI support
- **Analyze**: Breaking down complex problems into components
- **Evaluate**: Comparing different approaches and trade-offs
- **Create**: Independent problem-solving with minimal assistance

## Success Metrics

### Learning Effectiveness
- **Proficiency Progression**: Users advance from beginner to intermediate/advanced on tracked concepts
- **Reduced Repetition**: Decrease in identical question patterns over time
- **Task Independence**: Gradual reduction in AI assistance needed for previously delegated tasks

### Engagement Metrics
- Number of learning modules completed
- Time spent in focused learning sessions
- Consistency of weekly learning engagement

## Technical Requirements

### Backend Requirements
- **Conversation Analysis**: NLP processing of conversation history
- **Pattern Recognition**: Machine learning models for identifying repetitive queries
- **Learning Path Generation**: AI-powered curriculum creation
- **Progress Tracking**: User proficiency and learning analytics

### Frontend Requirements
- **Knowledge Visualization**: Interactive knowledge maps and progress charts
- **Learning Interface**: Engaging UI for flashcards, quizzes, and explanations
- **Progress Dashboard**: Clear visualization of learning journey
- **Responsive Design**: Works seamlessly across devices

### Data Requirements
- **Conversation Storage**: Secure storage and analysis of user conversations
- **Learning Analytics**: Tracking of user progress and proficiency levels
- **Content Generation**: Dynamic creation of learning materials
- **Privacy Protection**: User data protection and consent management

## Constraints
- Must integrate with existing Claude web app design language
- Must respect user privacy and data protection requirements
- Must provide immediate value while building long-term learning habits
- Must scale to handle large volumes of conversation data

## Success Criteria
1. Users can see clear visualization of their knowledge gaps and strengths
2. Learning interventions are relevant and based on actual usage patterns
3. Users demonstrate measurable improvement in independently handling previously delegated tasks
4. The system reduces repetitive questioning patterns over time
5. Users engage consistently with weekly learning sessions
