from .models import Plant
def recommend_plants(user_input):
    """
    Intelligent plant recommendation algorithm based on user input
    """
    plants = Plant.objects.all()
    
    # Filter by basic criteria
    if user_input.get('plant_type'):
        plants = plants.filter(plant_type=user_input['plant_type'])
    
    if user_input.get('difficulty'):
        plants = plants.filter(difficulty=user_input['difficulty'])
    
    if user_input.get('sunlight_hours'):
        plants = plants.filter(sunlight_hours__lte=user_input['sunlight_hours'])
    
    if user_input.get('sunlight_type'):
        plants = plants.filter(sunlight_type=user_input['sunlight_type'])
    
    if user_input.get('watering_level'):
        plants = plants.filter(watering_level=user_input['watering_level'])
    
    if user_input.get('toxic_to_pets') is not None:
        plants = plants.filter(toxic_to_pets=not user_input['toxic_to_pets'])
    
    # Score plants based on how well they match the criteria
    scored_plants = []
    for plant in plants:
        score = 0
        
        # Exact matches
        if user_input.get('plant_type') == plant.plant_type:
            score += 3
        if user_input.get('difficulty') == plant.difficulty:
            score += 2
        if user_input.get('sunlight_type') == plant.sunlight_type:
            score += 2
        if user_input.get('watering_level') == plant.watering_level:
            score += 3
        
        # Range matches
        if user_input.get('sunlight_hours'):
            if plant.sunlight_hours <= user_input['sunlight_hours']:
                score += 1
        
        # Additional scoring for pet safety if requested
        if user_input.get('toxic_to_pets') is not None and not plant.toxic_to_pets:
            score += 2
        
        scored_plants.append((plant, score))
    
    # Sort by score descending
    scored_plants.sort(key=lambda x: x[1], reverse=True)
    
    return [plant for plant, score in scored_plants]