"""Sidebar UI component for agent management."""

import streamlit as st
import json
import os
from typing import Optional

from ma_discussion.agents.base import CustomAgent
from ma_discussion.agents.coordinator import CoordinatorAgent
from ma_discussion.agents.factory import generate_task_force
from ma_discussion.constants import (
    COORDINATOR_ARCHETYPES,
    DATA_DIR,
    DEFAULT_TASKFORCE_FILE
)
from ma_discussion.ui.state import AppState

def show_agent_management(state: AppState) -> None:
    """Show the agent management section in the sidebar.
    
    Args:
        state: Application state
    """
    st.header("Agent Management")
    
    # Coordinator archetype selector
    st.subheader("Coordinator Settings")
    state.coordinator_archetype = st.selectbox(
        "Default Coordinator Style",
        options=COORDINATOR_ARCHETYPES,
        format_func=lambda x: x.title(),
        help="Choose the coordination style for auto-generated teams"
    )
    
    # Auto-generate task force section
    st.subheader("🤖 Auto-Generate Task Force")
    with st.form("generate_task_force"):
        scenario = st.text_area(
            "Describe your task or scenario",
            placeholder="e.g., Analyze the impact of AI on healthcare"
        )
        auto_team_model = st.selectbox(
            "Model for team generation",
            options=state.ollama_models
        )
        generate = st.form_submit_button("Generate Specialized Team")
        
        if generate and scenario:
            try:
                agents_list, system_prompt = generate_task_force(scenario, auto_team_model)
                state.last_system_prompt = system_prompt
                state.clear_agents()
                
                for agent_dict in agents_list:
                    name = agent_dict.get("name") or agent_dict.get("role")
                    role = agent_dict.get("role", "Expert")
                    prompt = agent_dict.get("prompt", "You are a helpful expert.")
                    
                    # Check if this should be a coordinator
                    is_coordinator = any(
                        term in role.lower()
                        for term in ["coordinator", "facilitator", "moderator", "mediator"]
                    )
                    
                    if is_coordinator:
                        agent = CoordinatorAgent(
                            name=name,
                            role=role,
                            archetype=state.coordinator_archetype,
                            base_prompt=prompt,
                            model=auto_team_model
                        )
                        state.coordinator = agent
                        st.success(f"Created {state.coordinator_archetype.title()} coordinator: {name}")
                    else:
                        agent = CustomAgent(name, role, prompt, auto_team_model)
                        st.success(f"Added standard agent: {name}")
                    
                    state.add_agent(agent)
                
                st.success(f"Created specialized task force with {len(agents_list)} agents!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating task force: {str(e)}")
    
    # Manual agent creation
    st.subheader("🎭 Add Single Agent")
    with st.form("add_agent"):
        agent_name = st.text_input("Agent Name")
        agent_role = st.text_input("Agent Role")
        
        # Role templates
        role_templates = {
            "Analyst": "You analyze data and situations systematically.",
            "Devil's Advocate": "You deliberately take opposing viewpoints to test arguments.",
            "Synthesizer": "You look for ways to integrate diverse viewpoints.",
            "Storyteller": "You use narratives and examples to illustrate points.",
            "Futurist": "You consider long-term implications and trends.",
            "Ethicist": "You focus on moral and ethical dimensions.",
            "Coordinator": "You guide discussions and help reach consensus."
        }
        
        template_choice = st.selectbox(
            "Personality Template",
            options=list(role_templates.keys())
        )
        
        agent_prompt = st.text_area(
            "Agent Instructions/Personality",
            value=role_templates[template_choice],
            height=150
        )
        
        agent_model = st.selectbox("Ollama Model", options=state.ollama_models)
        
        submit_agent = st.form_submit_button("Add Agent")
        
        if submit_agent:
            if not agent_name:
                st.error("Please enter an agent name")
            elif not agent_role:
                st.error("Please enter an agent role")
            elif not agent_prompt:
                st.error("Please enter agent instructions")
            else:
                if template_choice == "Coordinator":
                    agent = CoordinatorAgent(
                        name=agent_name,
                        role=agent_role,
                        archetype=state.coordinator_archetype,
                        base_prompt=agent_prompt,
                        model=agent_model
                    )
                    state.coordinator = agent
                else:
                    agent = CustomAgent(
                        name=agent_name,
                        role=agent_role,
                        base_prompt=agent_prompt,
                        model=agent_model
                    )
                state.add_agent(agent)
                st.success(f"Added agent: {agent_name}")
                st.rerun()
    
    # Current agents list
    if state.agents:
        st.subheader("Current Agents")
        for i, agent in enumerate(state.agents):
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{agent.name}** ({agent.role})")
                edited_prompt = st.text_area(
                    "Edit Prompt",
                    value=agent.base_prompt,
                    key=f"prompt_{i}",
                    height=100
                )
                
                if st.button("Update Prompt", key=f"update_{i}"):
                    agent.base_prompt = edited_prompt
                    st.success(f"Updated prompt for {agent.name}")
                    st.rerun()
            
            with col2:
                if st.button(f"Remove {agent.name}", key=f"remove_{i}"):
                    state.remove_agent(agent)
                    st.rerun()
    
    # Clear all agents button
    if st.button("Clear All Agents"):
        state.clear_agents()
        state.clear_conversation()
        st.rerun()
    
    # Save/Load Task Force
    st.subheader("💾 Save/Load Task Force")
    save_fn = st.text_input("Save as filename", value=DEFAULT_TASKFORCE_FILE)
    if st.button("Save Task Force"):
        if not state.agents:
            st.warning("No agents to save!")
        else:
            save_task_force(state, save_fn)
    
    load_fn = st.text_input("Load from filename", value=DEFAULT_TASKFORCE_FILE)
    if st.button("Load Task Force"):
        load_task_force(state, load_fn)

def save_task_force(state: AppState, filename: str) -> None:
    """Save the current set of agents to a JSON file.
    
    Args:
        state: Application state
        filename: Target filename
    """
    agents_out = []
    for agent in state.agents:
        agents_out.append({
            "name": agent.name,
            "role": agent.role,
            "prompt": agent.base_prompt,
            "model": agent.model,
            "is_coordinator": isinstance(agent, CoordinatorAgent)
        })
    
    # Create data directory if needed
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)
    
    with open(filepath, "w") as f:
        json.dump(agents_out, f, indent=2)
    st.success(f"Task force saved to {filepath}")

def load_task_force(state: AppState, filename: str) -> None:
    """Load a set of agents from a JSON file.
    
    Args:
        state: Application state
        filename: Source filename
    """
    filepath = os.path.join(DATA_DIR, filename)
    
    try:
        with open(filepath) as f:
            agents_in = json.load(f)
        
        state.clear_agents()
        
        for ad in agents_in:
            if ad.get("is_coordinator"):
                agent = CoordinatorAgent(
                    ad["name"],
                    ad["role"],
                    state.coordinator_archetype,
                    ad["prompt"],
                    ad["model"]
                )
                state.coordinator = agent
            else:
                agent = CustomAgent(
                    ad["name"],
                    ad["role"],
                    ad["prompt"],
                    ad["model"]
                )
            state.add_agent(agent)
            
        st.success(f"Loaded {len(agents_in)} agents from {filepath}")
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to load: {str(e)}")

def show_sidebar(state: Optional[AppState] = None) -> None:
    """Show the complete sidebar UI.
    
    Args:
        state: Optional application state, will use st.session_state if not provided
    """
    if state is None:
        if "app_state" not in st.session_state:
            st.session_state.app_state = AppState()
        state = st.session_state.app_state
    
    show_agent_management(state) 