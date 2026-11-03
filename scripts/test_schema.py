from src.schema import CVData

good = '{"name": "Asha", "email": null, "skills": ["Python"], "experience": []}'
print(CVData.model_validate_json(good))

bad = '{"skills": "Python"}'
try:
    CVData.model_validate_json(bad)
except Exception as e:
    print("FAIL (idhu expected):", e)
