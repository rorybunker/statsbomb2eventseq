import pandas as pd

# Define the field zones based on the pitch division
def get_field_zone(x, y):
    # Calculate the zone indices based on the pitch division
    x_zone = int(x * 3)
    y_zone = int(y * 6)
    
    # Define the field zones based on the zone indices
    zones = [
        ['A1', 'A2', 'A3'],
        ['B1', 'B2', 'B3'],
        ['C1', 'C2', 'C3'],
        ['D1', 'D2', 'D3'],
        ['E1', 'E2', 'E3'],
        ['F1', 'F2', 'F3'],
    ]
    
    # Return the field zone based on the zone indices
    return zones[y_zone][x_zone]


# Load the Statsbomb data from a CSV file
# With columns ,50_50,bad_behaviour_card,ball_receipt_outcome,ball_recovery_offensive,ball_recovery_recovery_failure,block_deflection,block_offensive,block_save_block,carry_end_location,clearance_aerial_won,clearance_body_part,clearance_head,clearance_left_foot,clearance_other,clearance_right_foot,counterpress,dribble_no_touch,dribble_nutmeg,dribble_outcome,dribble_overrun,duel_outcome,duel_type,duration,foul_committed_advantage,foul_committed_card,foul_committed_offensive,foul_committed_penalty,foul_committed_type,foul_won_advantage,foul_won_defensive,foul_won_penalty,goalkeeper_body_part,goalkeeper_end_location,goalkeeper_lost_in_play,goalkeeper_outcome,goalkeeper_position,goalkeeper_punched_out,goalkeeper_shot_saved_off_target,goalkeeper_shot_saved_to_post,goalkeeper_success_in_play,goalkeeper_technique,goalkeeper_type,half_start_late_video_start,id,index,injury_stoppage_in_chain,interception_outcome,location,match_id,minute,miscontrol_aerial_won,off_camera,out,pass_aerial_won,pass_angle,pass_assisted_shot_id,pass_body_part,pass_cross,pass_cut_back,pass_deflected,pass_end_location,pass_goal_assist,pass_height,pass_inswinging,pass_length,pass_miscommunication,pass_no_touch,pass_outcome,pass_outswinging,pass_recipient,pass_shot_assist,pass_straight,pass_switch,pass_technique,pass_through_ball,pass_type,period,play_pattern,player,player_id,position,possession,possession_team,possession_team_id,related_events,second,shot_aerial_won,shot_body_part,shot_deflected,shot_end_location,shot_first_time,shot_follows_dribble,shot_freeze_frame,shot_key_pass_id,shot_one_on_one,shot_open_goal,shot_outcome,shot_redirect,shot_saved_off_target,shot_saved_to_post,shot_statsbomb_xg,shot_technique,shot_type,substitution_outcome,substitution_replacement,tactics,team,team_id,timestamp,type,under_pressure
data = pd.read_csv('world_cup_2022.csv', low_memory=False)

# Sort the data
data.sort_values(['match_id', 'period', 'timestamp'], inplace=True)

# Initialize variables for the current match and possession team
current_match_id = None
current_possession_team = None
current_sequence = []
current_possession = None

# Create an empty list to store the transformed data
transformed_data = []

# Iterate over the rows of the DataFrame
for _, row in data.iterrows():
    match_id = row['match_id']
    possession_team = row['possession_team']
    possession = row['possession']
    event = row['type']
    team = row['team']
    location = row['location']
    
    # Exclude defensive actions
    if team != possession_team and possession_team is not None:
        continue
    
    # Split the location string into coordinates
    location_x, location_y = map(float, location.split(','))
    
    # Get the field zone based on the coordinates
    field_zone = get_field_zone(location_x, location_y)
    
    # Check if possession has changed
    if current_match_id != match_id or current_possession_team != possession_team or current_possession != possession:
        # Add the current sequence to the transformed data
        transformed_data.append((current_sequence, 1 if any(event == 'Shot' for event in current_sequence) else -1, current_match_id, current_possession_team, current_possession, field_zone))
        
        # Start a new sequence
        current_sequence = [(event, field_zone)]
    else:
        # Continue the current sequence
        current_sequence.append((event, field_zone))
    
    current_match_id = match_id
    current_possession_team = possession_team
    current_possession = possession

# Add the last sequence to the transformed data
if current_sequence:
    transformed_data.append((current_sequence, 1 if any(event == 'Shot' for event in current_sequence) else -1, current_match_id, current_possession_team, current_possession, field_zone))

# Create a new data frame with the transformed data
transformed_df = pd.DataFrame(transformed_data, columns=['events', 'label', 'match_id', 'possession_team', 'possession', 'field_zone'])

# Save the transformed data frame to a new CSV file
transformed_df.to_csv('world_cup_2022_event_seqs.csv', index=False)
