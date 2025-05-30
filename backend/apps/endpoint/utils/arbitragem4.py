import sys
import os
import json
import requests
import time
import cmath

# Define the underlying assets
underlying = ["PETR4","VALE3", "BOVA11", "BBAS3", "BBDC4", "COGN3", "MGLU3", "ITUB4", "WEGE3", "EMBR3"]

call_bid = 'bid'  # change to bid/close if needed
put_ask = 'ask'  # change to ask/close if needed

# Define API key and headers
headers = {
    'Access-Token': 'NV0MENA0YZ9bgJA/Wf+F+tROe+eYX9SpUBuhmxNNkeIVuQKf+/wtVkYT4gGo0uvg--tTAJG2No3ZgblMOUkEql4g==--NzllMzczOTg2ZWI5ZmJlN2U2MjBmMDA3NGIxODcxOWQ='
}

# Define base URL for the new API endpoint
option_base_url = 'https://api.oplab.com.br/v3/market/options'

# Define base URL for the new API endpoint
spot_base_url = 'https://api.oplab.com.br/v3/market/stocks'

def fetch_underlying_data(underlying_symbols, max_retries=3, delay=5):
    all_data = []
    
    for symbol in underlying_symbols:
        url = f"{spot_base_url}/{symbol}"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Filter the data to include only the desired fields
                filtered_data = {
                    "symbol": data.get("symbol"),
                    "type": data.get("type"),
                    "name": data.get("name"),
                    "open": data.get("open"),
                    "high": data.get("high"),
                    "low": data.get("low"),
                    "close": data.get("close"),
                    "volume": data.get("volume"),
                    "financial_volume": data.get("financial_volume"),
                    "trades": data.get("trades"),
                    "bid": data.get("bid"),
                    "ask": data.get("ask"),
                    "category": data.get("category"),
                    "contract_size": data.get("contract_size"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "parent_symbol": symbol  # Add parent_symbol to the filtered data
                }
                
                all_data.append(filtered_data)  # Append filtered data for each symbol
                break  # Exit retry loop if successful
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                print(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
    
    return all_data

def fetch_option_data(underlying_symbols, max_retries=3, delay=5):
    all_data = []
    
    for symbol in underlying_symbols:
        url = f"{option_base_url}/{symbol}"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                # Add parent_symbol to each option in the data
                for option in data:
                    option['parent_symbol'] = symbol
                all_data.extend(data)  # Combine data from all symbols
                break  # Exit retry loop if successful
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                print(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Failed to retrieve data for {symbol} after {max_retries} attempts. Skipping...")
    
    return all_data

def save_raw_data_to_json(data, file_path):
    if not data:
        print("No data to save.")
        return
    
    # Save raw data to JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"Raw data saved to {file_path}")

def calculate_option_metrics(option, underlying_data):
    # Fetch the close price (spot_price) for the underlying asset
    parent_symbol = option.get('parent_symbol')
    spot_price = None

    # Find the underlying asset data for the parent_symbol
    for underlying_asset in underlying_data:
        if underlying_asset['symbol'] == parent_symbol:
            spot_price = underlying_asset.get('ask')
            break

    # If spot_price is not found, default to 0
    if spot_price is None:
        print(f"Warning: Could not find spot price for {parent_symbol}. Defaulting to 0.")
        spot_price = 0

    # Use the spot_price for calculations
    close_price = option.get(call_bid, 0)  # Change to bid if needed
    strike = option.get('strike', 0)
    days_to_maturity = option.get('days_to_maturity', 0)

    # Determine moneyness
    if strike > spot_price:
        moneyness = 'OTM'
    else:
        moneyness = 'ITM'

    # Calculate intrinsic and extrinsic values
    intrinsic_value = max(spot_price - strike, 0)
    extrinsic_value = max(close_price - intrinsic_value, 0)
    protection = intrinsic_value / spot_price if spot_price != 0 else 0
    pm = spot_price - close_price
    embedded_interest = extrinsic_value / spot_price if spot_price != 0 else 0
    annual_return = (1 + embedded_interest)**(252 / days_to_maturity) - 1 if days_to_maturity != 0 else 0
    score = (protection * annual_return) if annual_return != 0 else 0

    # Add calculated metrics to the option
    option['moneyness'] = moneyness
    option['intrinsic_value'] = intrinsic_value
    option['extrinsic_value'] = extrinsic_value
    option['pm'] = pm
    option['protection'] = protection
    option['embedded_interest'] = embedded_interest
    option['annual_return'] = annual_return
    option['score'] = score
    option['spot_price'] = spot_price  # Add spot_price to the option for reference

    return option

def save_processed_data_to_json(data, file_path):
    if not data:
        print("No data to save.")
        return
    
    # Save processed data to JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"Processed data saved to {file_path}")



def filter_and_attach_puts(data):
    for call_option in data:
        if call_option['category'] == 'CALL' and 'days_to_maturity' in call_option:
            pm = call_option.get('pm', 0)  # Ensure pm is correctly accessed
            put_options = [
                put for put in data
                if put['category'] == 'PUT'
                and 'days_to_maturity' in put
                and put['days_to_maturity'] == call_option['days_to_maturity']
                and 'strike' in put
                and put['parent_symbol'] == call_option['parent_symbol']
            ]
            
            # Sort put options by strike
            put_options_sorted = sorted(put_options, key=lambda x: x['strike'])
            
            # Find the index of the first put option with strike >= pm
            split_index = next((i for i, put in enumerate(put_options_sorted) if put['strike'] >= pm), len(put_options_sorted))
            
            # Select 4 puts below and 4 puts above (or as many as available if less than 4)
            puts_below = put_options_sorted[max(0, split_index-4):split_index]
            puts_above = put_options_sorted[split_index:split_index+4]
            
            selected_puts = puts_below + puts_above
            call_option['puts'] = []
            # Calculate PUT-specific metrics and remove CALL-specific metrics
            for put in selected_puts:
                # Use the correct field for put_ask (close in this case)
                put_price = put.get(put_ask, 0)  # This will use the 'close' price of the PUT

                if put_price == 0:
                    continue  # Skip to the next PUT strike in the loop
                
                # Calculate PUT-specific metrics
                extrinsic_value_result = call_option['extrinsic_value'] - put_price
                spot_price = call_option.get('spot_price', 0)
                embedded_interest_result = extrinsic_value_result / spot_price if spot_price != 0 else 0
                days_to_maturity = call_option.get('days_to_maturity', 0)
                pm_result = pm + put_price  # Corrected calculation of pm_result
                total_risk = put.get('strike', 0) - pm_result
                total_gain = call_option['strike'] - pm_result
                spot_variation_to_max_return = (call_option['strike'] - spot_price) / spot_price
                spot_variation_to_stoploss = (put.get('strike', 0) - spot_price) / spot_price
                spot_variation_to_pm_result = (pm_result - spot_price) / spot_price
                pm_distance_to_profit = (call_option['strike'] - pm_result) / pm_result
                pm_distance_to_loss = (put.get('strike', 0) - pm_result) / pm_result
                if call_option['protection'] > 0:
                    intrinsic_protection = True
                else:
                    intrinsic_protection = False
                if pm_distance_to_loss > -0.001:
                    zero_risk = True
                else:
                    zero_risk = False
                if total_risk > -0.01 and total_gain > 0:                    
                    gain_to_risk_ratio = None
                elif total_risk <= -0.01:
                    gain_to_risk_ratio = total_gain / total_risk * (-1) if total_risk != 0 else 0
                
                # Handle potential complex number results
                try:
                    annual_return_result = (1 + embedded_interest_result)**(252 / days_to_maturity) - 1 if days_to_maturity != 0 else 0
                    if isinstance(annual_return_result, complex):
                        annual_return_result = annual_return_result.real
                except ValueError:
                    annual_return_result = 0

                try:
                    otm_annual_return_result = (1 + pm_distance_to_profit)**(252 / days_to_maturity) - 1 if days_to_maturity != 0 else 0
                    if isinstance(otm_annual_return_result, complex):
                        otm_annual_return_result = otm_annual_return_result.real
                except ValueError:
                    otm_annual_return_result = 0
                
                # Remove CALL-specific metrics from PUT
                for key in ['intrinsic_value', 'extrinsic_value', 'pm', 'protection', 'embedded_interest', 'annual_return', 'score']:
                    put.pop(key, None)
                
                # Add PUT-specific metrics
                put['extrinsic_value_result'] = extrinsic_value_result
                put['embedded_interest_result'] = embedded_interest_result
                put['pm_result'] = pm_result

                # Calculate combined score
                # Normalize spot_variation_to_max_return (lower is better)
                normalized_spot_variation_pm_result = 1 / (1 + abs(spot_variation_to_pm_result))  # Lower values are better
                # Normalize spot_variation_to_max_return (lower is better)
                normalized_spot_variation = 1 / (1 + abs(spot_variation_to_max_return))  # Lower values are better
                # Normalize pm_distance_to_loss (higher is better)
                normalized_pm_distance = pm_distance_to_loss  # Higher values are better
                # Normalize gain_to_risk_ratio (higher is better)
                normalized_gain_to_risk = gain_to_risk_ratio if gain_to_risk_ratio is not None else 0  # Higher values are better

                # Assign weights (adjust as needed)
                weight_spot_variation_pm_result = 0.50  # Weight for spot_variation_to_max_return
                weight_spot_variation = 0.10  # Weight for spot_variation_to_max_return
                weight_pm_distance = 0.05  # Weight for pm_distance_to_loss
                weight_gain_to_risk = 0.35  # Weight for gain_to_risk_ratio

                # Calculate combined score
                combined_score = (
                    weight_spot_variation_pm_result * normalized_spot_variation_pm_result +
                    weight_spot_variation * normalized_spot_variation +
                    weight_pm_distance * normalized_pm_distance +
                    weight_gain_to_risk * normalized_gain_to_risk
                )

                # Add combined score to the PUT
                put['combined_score'] = combined_score

                call_option['puts'].append({
                    "symbol": put.get('symbol', ''),
                    "category": put.get('category', ''),
                    "days_to_maturity": put.get('days_to_maturity', 0),
                    "market_maker": put.get('market_maker', False),
                    "maturity_type": put.get('maturity_type', ''),
                    "strike": put.get('strike', ''),
                    "open": put.get('open', 0),
                    "high": put.get('high', 0),
                    "low": put.get('low', 0),
                    "close": put.get('close', 0),
                    "ask": put.get('ask', 0),
                    "bid": put.get('bid', 0),
                    "bid_volume": put.get('bid_volume', 0),
                    "ask_volume": put.get('ask_volume', 0),
                    "financial_volume": put.get('financial_volume', 0),
                    "extrinsic_value_result": extrinsic_value_result,
                    "embedded_interest_result": embedded_interest_result,
                    "annual_return_result": annual_return_result,
                    "pm_result": pm_result,
                    "total_risk": total_risk,
                    "total_gain": total_gain,
                    "gain_to_risk_ratio": gain_to_risk_ratio,
                    "spot_variation_to_max_return": spot_variation_to_max_return,
                    "spot_variation_to_stoploss": spot_variation_to_stoploss,
                    "spot_variation_to_pm_result": spot_variation_to_pm_result,        
                    "pm_distance_to_profit": pm_distance_to_profit, 
                    "pm_distance_to_loss": pm_distance_to_loss, 
                    "otm_annual_return_result": otm_annual_return_result,              
                    "zero_risk": zero_risk,
                    "intrinsic_protection": intrinsic_protection,
                    "combined_score": combined_score  # Add combined score
                })

            # Sort the puts by combined_score in descending order
            call_option['puts'] = sorted(call_option['puts'], key=lambda x: x.get('combined_score', 0), reverse=True)

    return data

import os
import json

def save_to_json(data, current_directory):
    # Filter data to include only CALL options with associated PUTs
    filtered_data = [
        option for option in data
        if option['category'] == 'CALL' and len(option.get('puts', [])) > 0
    ]

    # Further filter based on financial_volume
    filtered_data = [
        option for option in filtered_data
        if option.get('financial_volume', 0) > 1000
    ]

    # Helper function to get the maximum gain_to_risk_ratio from puts
    def max_gain_to_risk_ratio(option):
        puts = option.get('puts', [])
        ratios = [put.get('gain_to_risk_ratio', 0) for put in puts if put.get('gain_to_risk_ratio') is not None]
        return max(ratios) if ratios else 0

    # Sort data based on the highest gain_to_risk_ratio of associated puts
    sorted_data = sorted(filtered_data, key=max_gain_to_risk_ratio, reverse=True)

    # Split data into intrinsic and OTM categories
    intrinsic_data = [option for option in sorted_data if option.get('intrinsic_value', 0) > 0]
    otm_data = [option for option in sorted_data if option.get('intrinsic_value', 0) == 0]

    # Function to save data for a specific category
    def save_category(category_data, prefix):
        if not category_data:
            print(f"No {prefix} data to save.")
            return

        # Categorize data based on days_to_maturity
        less_than_14 = [option for option in category_data if option.get('days_to_maturity', 0) < 14]
        between_15_and_30 = [option for option in category_data if 15 <= option.get('days_to_maturity', 0) < 30]
        between_30_and_60 = [option for option in category_data if 30 <= option.get('days_to_maturity', 0) < 60]
        more_than_60 = [option for option in category_data if option.get('days_to_maturity', 0) >= 60]

        # Define file paths for JSON outputs using the current directory
        less_than_14_path = os.path.join(current_directory, f"{prefix}_options_less_than_14_days.json")
        between_15_and_30_path = os.path.join(current_directory, f"{prefix}_options_between_15_and_30_days.json")
        between_30_and_60_path = os.path.join(current_directory, f"{prefix}_options_between_30_and_60_days.json")
        more_than_60_path = os.path.join(current_directory, f"{prefix}_options_more_than_60_days.json")

        # Save JSON data to the respective file paths
        with open(less_than_14_path, 'w', encoding='utf-8') as f:
            json.dump(less_than_14, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {less_than_14_path}")

        with open(between_15_and_30_path, 'w', encoding='utf-8') as f:
            json.dump(between_15_and_30, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {between_15_and_30_path}")

        with open(between_30_and_60_path, 'w', encoding='utf-8') as f:
            json.dump(between_30_and_60, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {between_30_and_60_path}")

        with open(more_than_60_path, 'w', encoding='utf-8') as f:
            json.dump(more_than_60, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {more_than_60_path}")

    # Save intrinsic data
    save_category(intrinsic_data, "intrinsic")

    # Save OTM data
    save_category(otm_data, "otm")

def main():
    # Fetch underlying data
    underlying_data = fetch_underlying_data(underlying)
    
    # Fetch raw option data
    raw_data = fetch_option_data(underlying)
    
    # Calculate option metrics for each option using the underlying data
    processed_data = [calculate_option_metrics(option, underlying_data) for option in raw_data]
    
    # Filter and attach puts to calls
    processed_data_with_puts = filter_and_attach_puts(processed_data)
    
    # Save processed data to JSON files based on days_to_maturity
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Define the export directory
    export_directory = os.path.join(current_directory, "export")
    save_to_json(processed_data_with_puts, export_directory)

if __name__ == "__main__":
    main()