import pandas as pd
import re

# Load the data
df = pd.read_csv('data/auction_data.csv')

# Filter only vehicles (exclude scooters and other non-vehicles)
df = df[df['title'].str.contains('RAM|JEEP|AUDI|KIA|NISSAN|CHEVROLET|BMW|FORD|BUICK|TOYOTA|HONDA|MAZDA|HYUNDAI|GMC|DODGE|CADILLAC', case=False, na=False)]

def score_vehicle(row):
    score = 100  # Start with perfect score
    
    # 1. Price evaluation (30 points)
    # Lower starting bid relative to reserve is better
    try:
        starting_bid = float(re.sub(r'[^\d.]', '', str(row['starting_bid'])))
        reserve_price = str(row['reserve_price'])
        
        if 'subject to seller approval' in reserve_price.lower():
            price_score = 15  # Uncertain reserve
        else:
            reserve = float(re.sub(r'[^\d.]', '', reserve_price))
            if starting_bid < reserve * 0.3:
                price_score = 30  # Great deal potential
            elif starting_bid < reserve * 0.5:
                price_score = 25  # Good deal
            elif starting_bid < reserve * 0.7:
                price_score = 20  # Fair
            else:
                price_score = 15  # Less attractive
    except:
        price_score = 15
    
    # 2. Condition evaluation (40 points)
    description = str(row['description']).lower() + ' ' + str(row['declarations']).lower()
    condition_score = 40
    
    # Major issues (deduct heavily)
    if 'engine noise' in description or 'engine will not turn over' in description:
        condition_score -= 20
    if 'transmission issues' in description:
        condition_score -= 20
    if 'frame damage' in description:
        condition_score -= 15
    if 'mechanical problems' in description and 'engine' not in description:
        condition_score -= 10
    if 'as is - where is' in description:
        condition_score -= 10
    
    # Moderate issues
    if 'claims total $10,000 - $14,999' in description:
        condition_score -= 12
    elif 'claims total $5000 - $9999' in description:
        condition_score -= 8
    elif 'claims total $3000 - $4999' in description:
        condition_score -= 5
    elif 'claims total $1000 - $2999' in description:
        condition_score -= 3
    
    # Minor issues
    if 'hail damage' in description:
        condition_score -= 5
    if 'panels repainted' in description:
        condition_score -= 3
    if 'exhaust modified' in description:
        condition_score -= 2
    if 'suspension requires repair' in description:
        condition_score -= 8
    if 'driveline noise' in description:
        condition_score -= 10
    
    # Positive features (add points)
    if 'leather' in description:
        condition_score += 3
    if 'sunroof' in description:
        condition_score += 2
    
    condition_score = max(0, condition_score)
    
    # 3. Odometer evaluation (30 points)
    odometer_str = str(row['odometer'])
    try:
        if 'unknown' in odometer_str.lower():
            odometer_score = 5
        else:
            km = float(re.sub(r'[^\d.]', '', odometer_str))
            if km < 100000:
                odometer_score = 30  # Excellent
            elif km < 150000:
                odometer_score = 25  # Very good
            elif km < 200000:
                odometer_score = 20  # Good
            elif km < 250000:
                odometer_score = 10  # Fair
            else:
                odometer_score = 5   # High mileage
    except:
        odometer_score = 15
    
    total_score = price_score + condition_score + odometer_score
    
    return {
        'total_score': total_score,
        'price_score': price_score,
        'condition_score': condition_score,
        'odometer_score': odometer_score
    }

# Calculate scores
scores = df.apply(score_vehicle, axis=1, result_type='expand')
df = pd.concat([df, scores], axis=1)

# Sort by total score
df = df.sort_values('total_score', ascending=False)

# Display results
print("=" * 120)
print("VEHICLE RANKING - BEST TO WORST BUYING OPTIONS")
print("=" * 120)
print("\nScoring System:")
print("  • Price (30 pts): Lower starting bid vs reserve = better deal")
print("  • Condition (40 pts): Clean vehicles with features = higher score")
print("  • Odometer (30 pts): Lower mileage = better score")
print("=" * 120)

print("\n🏆 TOP 20 BEST VEHICLES TO BUY:\n")
for idx, (_, row) in enumerate(df.head(20).iterrows(), 1):
    print(f"{idx}. SCORE: {row['total_score']:.0f}/100")
    print(f"   📋 LOT: {row['lot_number']}")
    print(f"   🚗 {row['title']}")
    print(f"   💰 Starting Bid: {row['starting_bid']} | Reserve: {row['reserve_price']}")
    print(f"   🛣️  Odometer: {row['odometer']}")
    print(f"   ⚙️  Engine: {row['engine']}")
    print(f"   ⭐ Breakdown: Price={row['price_score']:.0f}/30, Condition={row['condition_score']:.0f}/40, Odometer={row['odometer_score']:.0f}/30")
    
    # Show key issues if any
    issues = []
    desc_lower = str(row['declarations']).lower()
    if 'mechanical' in desc_lower:
        issues.append("⚠️ Mechanical Issues")
    if 'hail' in desc_lower:
        issues.append("⚠️ Hail Damage")
    if 'claims' in desc_lower:
        issues.append("⚠️ Insurance Claims")
    
    if issues:
        print(f"   ⚠️  Issues: {', '.join(issues)}")
    
    # Show positive features
    features = []
    if 'leather' in str(row['options']).lower():
        features.append("✓ Leather")
    if 'sunroof' in str(row['options']).lower():
        features.append("✓ Sunroof")
    if '4x4' in str(row['options']).lower():
        features.append("✓ 4X4")
    
    if features:
        print(f"   ✨ Features: {', '.join(features)}")
    
    print()

print("\n" + "=" * 120)
print("⚠️  BOTTOM 10 WORST VEHICLES TO AVOID:\n")
for idx, (_, row) in enumerate(df.tail(10).iterrows(), 1):
    print(f"{idx}. SCORE: {row['total_score']:.0f}/100")
    print(f"   📋 LOT: {row['lot_number']}")
    print(f"   🚗 {row['title']}")
    print(f"   💰 Starting Bid: {row['starting_bid']} | Reserve: {row['reserve_price']}")
    print(f"   🛣️  Odometer: {row['odometer']}")
    print(f"   ⚠️  Why Avoid: Score={row['price_score']:.0f}/30 price, {row['condition_score']:.0f}/40 condition, {row['odometer_score']:.0f}/30 odometer")
    print()

# Save ranked list to CSV
df[['page', 'lot_number', 'title', 'starting_bid', 'reserve_price', 'odometer', 'engine', 
    'total_score', 'price_score', 'condition_score', 'odometer_score', 'declarations', 'options']].to_csv(
    'data/ranked_vehicles.csv', index=False
)

print("=" * 120)
print(f"\n✅ Full ranked list saved to: data/ranked_vehicles.csv")
print(f"📊 Total vehicles ranked: {len(df)}")
