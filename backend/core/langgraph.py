from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class EdTechWorkflow:
    def __init__(self, teacher_agent, quiz_agent, revision_agent, vector_store):
        self.teacher_agent = teacher_agent
        self.quiz_agent = quiz_agent
        self.revision_agent = revision_agent
        self.vector_store = vector_store
    
    def _build_graph(self) -> StateGraph:
        """Build the workflow graph"""
        graph = StateGraph()
        
        # Add nodes
        graph.add_node("route_query", self._route_query)
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("teacher_response", self._teacher_response)
        graph.add_node("quiz_response", self._quiz_response)
        graph.add_node("revision_response", self._revision_response)
        graph.add_node("format_output", self._format_output)
        
        # Add edges
        graph.add_edge("route_query", "retrieve_context")
        
        # Conditional routing based on mode
        graph.add_conditional_edges(
            "retrieve_context",
            self._decide_agent,
            {
                "teacher": "teacher_response",
                "quiz": "quiz_response", 
                "revision": "revision_response"
            }
        )
        
        graph.add_edge("teacher_response", "format_output")
        graph.add_edge("quiz_response", "format_output")
        graph.add_edge("revision_response", "format_output")
        graph.add_edge("format_output", END)
        
        graph.set_entry_point("route_query")
        
        return graph
    
    async def process_query(
        self,
        query: str,
        mode: str,
        student_id: str,
        file_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Process student query through the workflow"""
        
        try:
            # 1. Retrieve context
            search_results = self.vector_store.similarity_search(query, k=5)
            context_docs = [doc for doc, score in search_results]
            
            # 2. Choose agent based on mode
            if mode.lower() in ["learn", "explain", "teach"]:
                agent = self.teacher_agent
            elif mode.lower() in ["quiz", "test", "questions"]:
                agent = self.quiz_agent
            elif mode.lower() in ["revision", "review", "summary"]:
                agent = self.revision_agent
            else:
                agent = self.teacher_agent  # Default
            
            # 3. Process with selected agent
            result = await agent.process(query, context_docs)
            
            return {
                "content": result.get("content", "No response generated"),
                "agent_type": result.get("agent_type", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "sources": result.get("sources", []),
                "mode": mode
            }
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {
                "content": "I apologize, but I encountered an error processing your request.",
                "agent_type": "error",
                "confidence": 0.0,
                "sources": []
            }
    
    async def _execute_graph(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute graph nodes sequentially (simplified execution)"""
        state = initial_state.copy()
        
        # Route query
        state = await self._route_query(state)
        
        # Retrieve context
        state = await self._retrieve_context(state)
        
        # Decide and execute agent
        agent_choice = self._decide_agent(state)
        
        if agent_choice == "teacher":
            state = await self._teacher_response(state)
        elif agent_choice == "quiz":
            state = await self._quiz_response(state)
        elif agent_choice == "revision":
            state = await self._revision_response(state)
        
        # Format output
        state = await self._format_output(state)
        
        return state
    
    async def _route_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initial query routing and validation"""
        # Could add query preprocessing, intent detection, etc.
        return state
    
    async def _retrieve_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context from vector store"""
        query = state["query"]
        file_ids = state["file_ids"]
        
        # Build filter for specific files if provided
        filter_dict = None
        if file_ids:
            filter_dict = {"file_id": file_ids[0]}  # Simplified - could handle multiple files
        
        # Search for relevant documents
        search_results = self.vector_store.similarity_search(
            query, 
            k=5,
            filter_dict=filter_dict
        )
        
        # Extract documents from results
        context_docs = [doc for doc, score in search_results]
        state["context_docs"] = context_docs
        
        return state
    
    def _decide_agent(self, state: Dict[str, Any]) -> str:
        """Decide which agent to use based on mode"""
        mode = state["mode"].lower()
        
        if mode in ["learn", "explain", "teach"]:
            return "teacher"
        elif mode in ["quiz", "test", "questions"]:
            return "quiz"
        elif mode in ["revision", "review", "summary"]:
            return "revision"
        else:
            return "teacher"  # Default
    
    async def _teacher_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate teacher response"""
        response = await self.teacher_agent.process(
            state["query"],
            state["context_docs"]
        )
        state["agent_response"] = response
        return state
    
    async def _quiz_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quiz response"""
        response = await self.quiz_agent.process(
            state["query"],
            state["context_docs"]
        )
        state["agent_response"] = response
        return state
    
    async def _revision_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate revision response"""
        response = await self.revision_agent.process(
            state["query"],
            state["context_docs"]
        )
        state["agent_response"] = response
        return state
    
    async def _format_output(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Format final response"""
        agent_response = state["agent_response"]
        
        final_response = {
            "content": agent_response.get("content", "No response generated"),
            "agent_type": agent_response.get("agent_type", "unknown"),
            "confidence": agent_response.get("confidence", 0.0),
            "sources": agent_response.get("sources", []),
            "mode": state["mode"]
        }
        
        state["final_response"] = final_response
        return state