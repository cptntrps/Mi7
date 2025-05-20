"""Main UI component for the discussion interface."""

import streamlit as st
from typing import Optional

from ma_discussion.ui.state import AppState
from ma_discussion.ui.sidebar import show_sidebar

def show_discussion_interface(state: Optional[AppState] = None) -> None:
    """Show the main discussion interface.
    
    Args:
        state: Optional application state, will use st.session_state if not provided
    """
    if state is None:
        if "app_state" not in st.session_state:
            st.session_state.app_state = AppState()
        state = st.session_state.app_state
    
    # Page config
    st.set_page_config(
        page_title="Multi-Agent Discussion",
        page_icon="🤖",
        layout="wide"
    )
    
    # Sidebar (should be shown first, outside of columns)
    with st.sidebar:
        show_sidebar(state)
    
    # Main content area
    st.title("🤖 Multi-Agent Discussion")
    
    # Create two columns for the main content
    left_col, right_col = st.columns([2, 3])
    
    with left_col:
        # Discussion configuration
        st.subheader("Start a Discussion")
        discussion_topic = st.text_area(
            "Discussion Topic",
            placeholder="Enter a topic or question for discussion...",
            height=100
        )
        
        discussion_rounds = st.number_input(
            "Number of Discussion Rounds",
            min_value=1,
            max_value=10,
            value=3
        )
        
        show_thinking = st.checkbox(
            "Show Agent Thinking Process",
            value=True,
            help="Display each agent's internal reasoning process"
        )
        
        if st.button("Run Discussion", type="primary"):
            if not state.agents:
                st.error("Please add some agents using the sidebar first!")
            elif not discussion_topic:
                st.error("Please enter a discussion topic!")
            else:
                st.success(f"Starting discussion with {len(state.agents)} agents...")
                # Clear previous conversation
                state.clear_conversation()
                
                # Add system message
                state.add_message({
                    "role": "system",
                    "content": f"Starting discussion on: {discussion_topic}\nNumber of rounds: {discussion_rounds}"
                })
                
                # Run discussion rounds
                for round_num in range(discussion_rounds):
                    st.markdown(f"#### Round {round_num + 1}")
                    
                    # Each agent takes a turn
                    for agent in state.agents:
                        # Show thinking process if enabled
                        if show_thinking:
                            thinking = agent.think(discussion_topic)
                            with st.expander(f"🧠 {agent.name}'s Thinking Process"):
                                st.markdown(thinking)
                        
                        # Generate and show response
                        response = agent.process_message(discussion_topic, state.conversation_history)
                        state.add_message({
                            "role": "assistant",
                            "content": response,
                            "avatar": "🤖"
                        })
                        
                    # If this is the last round and we have a coordinator, generate summary
                    if round_num == discussion_rounds - 1 and state.coordinator:
                        summary = state.coordinator.summarize_discussion(state.conversation_history)
                        state.add_message({
                            "role": "system",
                            "content": f"Discussion Summary:\n{summary}",
                            "avatar": "👑"
                        })
                
                st.success(f"Completed {discussion_rounds} rounds of discussion!")
                st.rerun()
    
    with right_col:
        # Display conversation history
        st.header("Discussion")
        for msg in state.conversation_history:
            with st.chat_message(msg["role"], avatar=msg.get("avatar")):
                st.markdown(msg["content"])
        
        # Display streaming message if any
        if state.current_streaming_message:
            with st.chat_message("assistant"):
                st.markdown(state.current_streaming_message)
        
        # Control buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Chat"):
                state.clear_conversation()
                st.rerun()
        
        with col2:
            if st.button("Generate Summary"):
                if state.coordinator and state.conversation_history:
                    summary = state.coordinator.summarize_discussion(state.conversation_history)
                    st.info("Discussion Summary:\n\n" + summary)
                else:
                    st.warning("Cannot generate summary: No coordinator or empty discussion.") 