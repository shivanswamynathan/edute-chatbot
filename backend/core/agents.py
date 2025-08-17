from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from typing import List, Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, llm_wrapper, prompt_file: str):
        self.llm = llm_wrapper
        self.prompt_template = self._load_prompt(prompt_file)
    
    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt from file"""
        try:
            with open(f"backend/prompts/{prompt_file}", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.warning(f"Prompt file {prompt_file} not found, using default")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        return "You are a helpful educational assistant. Answer the student's question based on the provided context."
    
    async def process(
        self, 
        query: str, 
        context_docs: List[Document], 
        student_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process student query with context"""
        context = self._format_context(context_docs)
        
        formatted_prompt = self.prompt_template.format(
            query=query,
            context=context,
            student_info=student_info or {}
        )
        
        messages = [
            SystemMessage(content="You are an expert educational tutor."),
            HumanMessage(content=formatted_prompt)
        ]
        
        response = await self.llm.generate_response(messages)
        
        return {
            "content": response,
            "agent_type": self.__class__.__name__,
            "confidence": 0.8,  # Could implement confidence scoring
            "sources": [doc.metadata.get("source", "Unknown") for doc in context_docs]
        }
    
    def _format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents as context"""
        if not documents:
            return "No relevant context found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            context_parts.append(f"Context {i} (from {source}):\n{doc.page_content}")
        
        return "\n\n".join(context_parts)

class TeacherAgent(BaseAgent):
    def __init__(self, llm_wrapper):
        super().__init__(llm_wrapper, "teacher.txt")
    
    def _get_default_prompt(self) -> str:
        return """You are an expert teacher helping a student understand concepts. 

Context: {context}

Student's Question: {query}

Please provide a clear, comprehensive explanation that:
1. Directly answers the student's question
2. Uses simple language appropriate for the student's level
3. Includes relevant examples when helpful
4. Encourages further learning

Your response:"""

class QuizAgent(BaseAgent):
    def __init__(self, llm_wrapper):
        super().__init__(llm_wrapper, "quiz.txt")
    
    def _get_default_prompt(self) -> str:
        return """You are a quiz generator creating educational questions for students.

Context: {context}

Based on the context, generate quiz questions related to: {query}

Create 3-5 multiple choice questions that:
1. Test understanding of key concepts
2. Are clear and unambiguous
3. Have one correct answer and 3 plausible distractors
4. Include explanations for correct answers

Format each question as:
Q: [Question text]
A) [Option A]
B) [Option B] 
C) [Option C]
D) [Option D]
Correct Answer: [Letter]
Explanation: [Why this is correct]

Your quiz:"""

class RevisionAgent(BaseAgent):
    def __init__(self, llm_wrapper):
        super().__init__(llm_wrapper, "revision.txt")
    
    def _get_default_prompt(self) -> str:
        return """You are a revision assistant helping students review key concepts.

Context: {context}

Topic for revision: {query}

Create a comprehensive revision summary that includes:
1. Key concepts and definitions
2. Important facts and figures
3. Common patterns or relationships
4. Memory aids or mnemonics where helpful
5. Practice questions for self-testing

Make it concise but complete for effective revision.

Your revision summary:"""