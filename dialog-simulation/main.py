import json
import jsonlines
import os
from agents.agent import Agent
from utils.utils import id_to_ordinal, log_and_print
import argparse
import random
import pandas as pd
from utils.keys import API_KEYS, ORGANIZATION_IDS

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run a dialog simulation.')
    parser.add_argument('--config_name', type=str, default='default',
                        help='The descriptive name of the simulation configuration, e.g. "speed_date". It should have a corresponding folder under "config/".')
    parser.add_argument('--repeats', type=int, default=1, help='The number of times to repeat the simulation.')
    parser.add_argument('--LM', type=str, default='gpt-4', help='The language model to use for text generation.')
    parser.add_argument("--api_key_id", help="The API key to use.", default="CCB")

    args = parser.parse_args()
    config_name = args.config_name
    repeats = args.repeats
    LM = args.LM
    api_key_id = args.api_key_id

    api_key = API_KEYS[api_key_id]
    org_id = ORGANIZATION_IDS[api_key_id]

    # Load town areas and people from JSON file
    config_dir = f'config/{config_name}'
    general_config_frn = f"{config_dir}/general.json"
    with open(general_config_frn, 'r') as fr:
        general_config = json.load(fr)
        temperature = general_config['temperature']
        scenario_description = general_config['scenario_description']
        max_turns = general_config['max_turns_each_iteration']
        max_tokens_each_msg = general_config['max_tokens_each_message']
    agents_config_frn = f"{config_dir}/agents.json"
    with open(agents_config_frn, 'r') as fr:
        town_people = json.load(fr)

    # Initialize agents
    male_agents = []
    female_agents = []
    agents = []
    log_dir = f'logs/{config_name}_{LM}'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    simulation_log = open(f'{log_dir}/simulation_log.txt', 'w')
    for agent_name, agent_description in town_people.items():
        new_agent = Agent(LM=LM,
                          api_key=api_key,
                          org_id=org_id,
                          name=agent_name,
                          description=agent_description)
        agents.append(new_agent)
        if new_agent.gender == "woman":
            female_agents.append(new_agent)
        elif new_agent.gender == "man":
            male_agents.append(new_agent)
        else:
            raise ValueError(f"Unknown gender: {new_agent.gender}")
        new_agent.memory_log = jsonlines.Writer(open(f'{log_dir}/{agent_name}_log.jsonl', 'w'), flush=True)
        log_and_print(simulation_log, f"{agent_name}:\n {new_agent.identity_prompt}\n\n")

    assert len(male_agents) == len(female_agents)
    n_agents_each_side = len(female_agents)

    # Start simulation loop
    for repeat in range(repeats):
        repeat_str = f"====================== REPEAT {repeat} ======================\n"
        log_and_print(simulation_log, repeat_str)

        # Introduce the scenario
        liking_score_dict = {}  # liking_score_dict[agent1_name][agent2_name] = how much agent1 likes agent2 (on a scale of 0 to 100)
        for agent in agents:
            scenario_description_prompt = scenario_description.replace("[OPPOSITE_GENDER]", agent.opposite_gender)
            agent.add_to_memory({"role": "user", "content": scenario_description_prompt})
            liking_score_dict[agent.name] = {}

        # Being the rotations
        for iteration in range(n_agents_each_side):  # A new iteration with 4 new pairings
            iteration_str = f"----------------------- ITERATION {iteration} -----------------------\n"
            log_and_print(simulation_log, iteration_str)

            iteration_ordinal = id_to_ordinal(iteration)

            # each pair of male and female agents has a conversation
            for male_agent, female_agent in zip(male_agents, female_agents):
                log_and_print(simulation_log, f"\nPaired agents: {male_agent.name}, {female_agent.name}\n")
                paired_agents = (male_agent, female_agent)

                for agent in paired_agents:
                    partner_agent = paired_agents[1 - paired_agents.index(agent)]
                    partner_name = partner_agent.name
                    partner_profession = partner_agent.profession
                    partner_age = partner_agent.age
                    new_pairing_prompt = f"Now, you are going to meet the {iteration_ordinal} {agent.opposite_gender}, {partner_name} ({partner_age} years old), {partner_profession}.\n"
                    log_and_print(simulation_log, new_pairing_prompt)
                    new_memory = {"role": "user", "content": new_pairing_prompt}
                    agent.add_to_memory(new_memory)

                # randomly choose a starting agent
                start_idx = random.choice([0, 1])
                first_agent = paired_agents[start_idx]
                second_agent = paired_agents[1 - start_idx]

                first_agent_msg, second_agent_msg = None, None

                # the current pair talks for a number of turns
                for turn in range(max_turns):
                    if turn == 0:  # first turn
                        instruction_prompt = 'What do you want to say to {}?\n(Note: 1. Say your part in the format of \'{}: "[your response]"\'.\n 2. Don\'t try to play {}.\n 3. Try to be casual, funny, dramatic, and not too formal. 4. Remember to stick to your own personality. You don\'t always have to be nice to everyone. \n 5. Don\'t always try to talk about work and collaboration. You can talk about hobbies, income, personality, ambititions, etc. Be creative!. 6. Your opening should be {} words max!)'
                    elif turn == max_turns - 1:  # last turn
                        instruction_prompt = '\n(Note that you only have 1 min left to talk to the current candidate!)'
                    else:
                        instruction_prompt = f"\n(Your reponse should be {max_tokens_each_msg} words max!)"

                    first_agent_instruction_prompt = instruction_prompt.format(second_agent.first_name,
                                                                               first_agent.first_name,
                                                                               second_agent.first_name,
                                                                               max_tokens_each_msg * 0.5)
                    first_agent_msg, _ = first_agent.converse(incoming_message=second_agent_msg,
                                                              partner_name=second_agent.first_name,
                                                              instructions=first_agent_instruction_prompt,
                                                              max_tokens=int(max_tokens_each_msg * 1.5),
                                                              temperature=temperature)

                    second_agent_instruction_prompt = instruction_prompt.format(first_agent.first_name,
                                                                                second_agent.first_name,
                                                                                first_agent.first_name,
                                                                                max_tokens_each_msg * 0.5)
                    second_agent_msg, _ = second_agent.converse(incoming_message=first_agent_msg,
                                                                partner_name=first_agent.first_name,
                                                                instructions=second_agent_instruction_prompt,
                                                                max_tokens=int(max_tokens_each_msg * 1.5),
                                                                temperature=temperature)

                    # log the conversation
                    log_and_print(simulation_log, f"{first_agent.name}: {first_agent_msg}\n")
                    log_and_print(simulation_log, f"{second_agent.name}: {second_agent_msg}\n")

                # get the score for the current pair
                first_agent_score, first_agent_expl = first_agent.get_liking_score_and_explanation(
                    second_agent.first_name)
                second_agent_score, second_agent_expl = second_agent.get_liking_score_and_explanation(
                    first_agent.first_name)
                # log the score
                first_agent_score_str = f"{first_agent.name}'s liking score for {second_agent.name}: {first_agent_score}\nExplanation: {first_agent_expl}\n"
                second_agent_score_str = f"{second_agent.name}'s liking score for {first_agent.name}: {second_agent_score}\nExplanation: {second_agent_expl}\n"
                log_and_print(simulation_log, first_agent_score_str)
                log_and_print(simulation_log, second_agent_score_str)

                liking_score_dict[first_agent.name][second_agent.name] = first_agent_score
                liking_score_dict[second_agent.name][first_agent.name] = second_agent_score

            # shift male_agents by one position to their right
            male_agents = male_agents[-1:] + male_agents[:-1]

        # print the liking scores as pandas dataframe

        liking_score_df = pd.DataFrame(liking_score_dict)

        # save the liking scores to a file
        liking_score_df.to_csv(f"{log_dir}/liking_scores_{repeat}.csv")

        log_and_print(simulation_log, f"----------------------- END OF REPEAT {repeat} -----------------------")

    # close log files
    simulation_log.close()
    for agent in agents:
        agent.memory_log.close()
