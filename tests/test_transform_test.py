def test_determine_relationships():
    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [1, 0]},
    ]
    object_data = {
        "relationships": {
            "to_the_left": ["is to the left of"],
            "to_the_right": ["is to the right of"],
            "in_front_of": ["is in front of"],
            "behind": ["is behind"],
        }
    }
    relationships = determine_relationships(objects, object_data)
    assert len(relationships) == 2
    assert "obj1 is to the left of and is in front of obj2." in relationships
    assert "obj2 is to the right of and is behind obj1." in relationships

    # Additional tests for transformed positions
    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [0, 1]},
    ]
    relationships = determine_relationships(objects, object_data)
    assert len(relationships) == 2
    assert "obj1 is in front of obj2." in relationships
    assert "obj2 is behind obj1." in relationships

    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [-1, 0]},
    ]
    relationships = determine_relationships(objects, object_data)
    assert len(relationships) == 2
    assert "obj1 is to the left of obj2." in relationships
    assert "obj2 is to the right of obj1." in relationships

    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [0, -1]},
    ]
    relationships = determine_relationships(objects, object_data)
    assert len(relationships) == 2
    assert "obj1 is behind obj2." in relationships
    assert "obj2 is in front of obj1." in relationships
