import json
import os
from agents.agent import Agent
from utils.text_generation import summarize_simulation
import argparse
import random

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run a dialog simulation.')
    parser.add_argument('--config_name', type=str, default='default', help='The descriptive name of the simulation configuration, e.g. "speed_date". It should have a corresponding folder under "config/".')
    parser.add_argument('--repeats', type=int, default=1, help='The number of times to repeat the simulation.')
    parser.add_argument('--LM', type=str, default='gpt-4', help='The language model to use for text generation.')

    args = parser.parse_args()
    config_name = args.config_name
    repeats = args.repeats
    LM = args.LM

    # Load town areas and people from JSON file
    config_dir = f'config/{config_name}'
    general_config_frn = f"{config_dir}/general.json"
    with open(general_config_frn, 'r') as fr:
        general_config = json.load(fr)
        temperature = general_config['temperature']
        scenario_description = general_config['scenario_description']
        max_turns = general_config['max_turns_each_iteration']
    agents_config_frn = f"{config_dir}/agents.json"
    with open(agents_config_frn, 'r') as fr:
        town_people = json.load(fr)

    # Initialize agents
    male_agents = []
    female_agents = []
    agents = []
    log_dir = f'logs/{config_name}'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    simulation_log = open(f'{log_dir}/simulation_log.txt', 'w')
    agent_logs = {}
    for agent_name, agent_description in town_people.items():
        new_agent = Agent(LM, agent_name, agent_description)
        agents.append(new_agent)
        if new_agent.gender == "woman":
            female_agents.append(new_agent)
        elif new_agent.gender == "man":
            male_agents.append(new_agent)
        else:
            raise ValueError(f"Unknown gender: {new_agent.gender}")
        agent_logs[agent_name] = open(f'{log_dir}/{agent_name}_log.json', 'w')

    assert len(male_agents) == len(female_agents)
    n_agents_each_side = len(female_agents)
    # print("Female agents:")
    # print(female_agents)
    # print("Male agents:")
    # print(male_agents)

    # Start simulation loop
    for repeat in range(repeats):
        repeat_str = f"====================== REPEAT {repeat} ======================\n"
        print(repeat_str)
        simulation_log.write(repeat_str)
        simulation_log.flush()

        for iteration in range(n_agents_each_side): # A new iteration with new pairings
            iteration_str = f"----------------------- ITERATION {iteration} -----------------------\n"
            print(iteration_str)
            simulation_log.write(iteration_str)

            for male_agent, female_agent in zip(male_agents, female_agents):
                # each pair of male and female agents has a conversation
                paired_agents = [male_agent, female_agent]

                # randomly choose a startng agent
                start_idx = random.choice([0,1])
                first_agent = paired_agents[start_idx]
                second_agent = paired_agents[1-start_idx]

                first_agent_initial_msg = scenario_description.replace("[OPPOSITE_GENDER]", first_agent.opposite_gender)
                second_agent_initial_msg = scenario_description.replace("[OPPOSITE_GENDER]", second_agent.opposite_gender)

                for turn in range(max_turns):
                    first_agent.converse(incoming_message, partner_name, instructions, max_tokens=512, temperature=0.5)





            # shift male_agents by one position to their right
            male_agents = male_agents[-1:] + male_agents[:-1]

        print(f"----------------------- SUMMARY FOR REPEAT {repeat} -----------------------")


    # close log files
    simulation_log.close()
    for agent in agents:
        agent_logs[agent.name].close()

