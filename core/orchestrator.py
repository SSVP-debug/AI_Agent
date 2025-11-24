from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.strategist import strategist_agent
from agents.writer import writer_agent

def run_pipeline(topic):

    print("[1] Planning...")
    plan = planner_agent(topic)

    print("[2] Research...")
    research = researcher_agent(topic)

    print("[3] Strategy...")
    strategy = strategist_agent(topic)

    print("[4] Final Writing...")
    final = writer_agent(topic, plan, research, strategy)

    return final
