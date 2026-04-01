from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import scraper, resume_parser, gap_analyzer, rewriter, cover_letter


def human_gate_node(state: AgentState) -> AgentState:
    # No terminal blocking — Streamlit UI handles approval via button
    # CLI mode sets human_approved=True before calling submit separately
    return state


def route_after_gate(state: AgentState) -> str:
    # In Streamlit mode the graph always stops here.
    # The UI submit button calls submitter.run() directly, outside the graph.
    return END


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("scrape_jd",      scraper.run)
    graph.add_node("parse_resume",   resume_parser.run)
    graph.add_node("analyze_gap",    gap_analyzer.run)
    graph.add_node("rewrite_resume", rewriter.run)
    graph.add_node("write_cover",    cover_letter.run)
    graph.add_node("human_gate",     human_gate_node)

    graph.set_entry_point("scrape_jd")
    graph.add_edge("scrape_jd",      "parse_resume")
    graph.add_edge("parse_resume",   "analyze_gap")
    graph.add_edge("analyze_gap",    "rewrite_resume")
    graph.add_edge("rewrite_resume", "write_cover")
    graph.add_edge("write_cover",    "human_gate")
    graph.add_conditional_edges("human_gate", route_after_gate)

    return graph.compile()