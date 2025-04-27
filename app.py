from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load baseline data
shot_df = pd.read_csv("data/shot_baseline.csv")
putt_df = pd.read_csv("data/putt_baseline.csv")

# Strip any unwanted spaces from the column names
shot_df.columns = shot_df.columns.str.strip()
putt_df.columns = putt_df.columns.str.strip()

# Convert to a dictionary with Distance as the key, and the other columns as values
shot_lookup = shot_df.set_index('Distance').to_dict(orient='index')
putt_lookup = putt_df.set_index('Distance').to_dict(orient='index')

# Function to get baseline value from the lookup
'''
def get_baseline(lie, distance):
    if lie == 'Green':
        return putt_lookup.get(distance, None)  # Use putt data for 'Green'
    else:
        return shot_lookup.get(lie, {}).get(distance, None)  # Use shot data for other lies
'''

def get_baseline(lie, distance):
    if lie == 'Green':
        # for putts your putt_lookup is also keyed by distance
        return putt_lookup.get(distance, {}).get('Baseline')  
        # <-- adjust 'Baseline' to whatever the column name is in putt_baseline.csv
    else:
        # look up the row by distance, then pick off the correct lie column
        return shot_lookup.get(distance, {}).get(lie)

# Function to calculate strokes gained
def strokes_gained_calculate(initial_lie, initial_distance, final_lie, final_distance, shot_df, putt_df):
    # Get baseline value for initial lie and distance
    start_value = get_baseline(initial_lie, initial_distance)
    
    # Get baseline value for final lie and distance
    final_value = get_baseline(final_lie, final_distance)

    # If either value is None, return error message
    if start_value is None or final_value is None:
        return None

    # Calculate strokes gained
    strokes_gained = start_value - (1 + final_value)

    # Format the output with the correct sign
    if strokes_gained > 0:
        result = f"Strokes Gained: +{strokes_gained:.3f}"
    else:
        result = f"Strokes Gained: {strokes_gained:.3f}"

    return result

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/calculate', methods=['POST'])
def calculate_strokes_gained():
    data = request.json
    start_lie = data['start_lie']
    start_dist = int(data['start_distance'])
    end_lie = data['end_lie']
    end_dist = int(data['end_distance'])

    # Get baseline values from the lookup dictionaries
    start_value = get_baseline(start_lie, start_dist)
    end_value = get_baseline(end_lie, end_dist)

    # Check for missing data
    if start_value is None or end_value is None:
        return jsonify({'error': 'Invalid input. Check lies or distances.'}), 400

    # Calculate strokes gained
    strokes_gained = start_value - end_value - 1  # Subtract 1 stroke for the shot taken

    return jsonify({'strokes_gained': round(strokes_gained, 3)})


if __name__ == '__main__':
    print("Starting the Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5211)

