import pandas as pd
from typing import List, Dict

class CompetencyData:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.df.fillna('', inplace=True)

    def get_competencies(self) -> List[str]:
        # Return unique, non-empty competencies
        return sorted(self.df['Competency Name'].dropna().unique())

    def get_designations(self, competency: str) -> List[str]:
        # Return all designations for a given competency, including those with empty competency name (continuation rows)
        # Find the first row with the given competency
        idx = self.df[self.df['Competency Name'] == competency].index
        if len(idx) == 0:
            return []
        start = idx[0]
        # Collect rows until the next non-empty competency name or end of file
        designations = []
        for i in range(start, len(self.df)):
            row = self.df.iloc[i]
            if i != start and row['Competency Name'] and row['Competency Name'] != competency:
                break
            designation = row['Designation Name']
            if designation and designation.strip():
                designations.append(designation.strip())
        return designations

    def get_skills_for_designation(self, competency: str, designation: str) -> Dict[str, List[str]]:
        # Find the first row for the competency
        idx = self.df[self.df['Competency Name'] == competency].index
        if len(idx) == 0:
            return {}
        start = idx[0]
        # Search for the row with the given designation within this competency block
        for i in range(start, len(self.df)):
            row = self.df.iloc[i]
            if i != start and row['Competency Name'] and row['Competency Name'] != competency:
                break
            if row['Designation Name'] == designation:
                skill_levels = ['Skills: Novice', 'Skills: Basic', 'Skills: Intermediate', 'Skills: Advanced', 'Skills: Expert']
                skills = {}
                for level in skill_levels:
                    val = row.get(level, '')
                    if isinstance(val, str) and val.strip() and val.strip() != '-':
                        skills[level] = [s.strip() for s in val.split(',') if s.strip()]
                    else:
                        skills[level] = []
                return skills
        return {}

    def get_certifications_for_designation(self, competency: str, designation: str) -> List[str]:
        filtered = self.df[(self.df['Competency Name'] == competency) & (self.df['Designation Name'] == designation)]
        if filtered.empty:
            return []
        val = filtered.iloc[0].get('Degrees & Certifications', '')
        if isinstance(val, str) and val.strip():
            # Split by common delimiters
            return [s.strip() for s in val.replace('+', ',').replace('Same as above', '').split(',') if s.strip()]
        return []
