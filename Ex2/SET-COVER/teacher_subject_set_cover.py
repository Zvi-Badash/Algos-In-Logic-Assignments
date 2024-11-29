from typing import Set, Dict
from dataclasses import dataclass

@dataclass
class Teacher:
    name: str
    subjects: Set[str]

    def __hash__(self):
        return hash(self.name + ''.join(sorted(self.subjects)))

    @classmethod
    def from_dict(cls, data: Dict) -> 'Teacher':
        """
        Create a Teacher instance from a dictionary.

        Args:
            data (Dict): Dictionary containing teacher data.

        Returns:
            Teacher: A new Teacher instance.
        """
        required_keys = {'name', 'subjects'}
        if not all(key in data for key in required_keys):
            raise ValueError(f"Missing required keys. Required: {required_keys}")
        
        return cls(
            name=data['name'],
            subjects=set(data['subjects'])
        )
        
@dataclass
class TeacherSubjectSetCover:
    """
    A class representing a teacher-subject set cover problem instance.

    Attributes:
        teachers (List[Teacher]): List of teachers.
        subjects (Set[str]): Set of subjects.
        k (int): Required number of teachers.
    """
    teachers: Set[Teacher]
    subjects: Set[str]
    k: int
    
    def __post_init__(self):
        self._validate_structure()

    def _validate_structure(self) -> None:
        """
        Validate the structure of the problem instance, ensuring:
        - Each teacher has a unique name.
        - There is at least one teacher.
        - k is a positive integer.
        """
        # Check for unique teacher names
        teacher_names = [teacher.name for teacher in self.teachers]
        if len(teacher_names) != len(set(teacher_names)):
            raise ValueError("Each teacher must have a unique name.")

        # Check for at least one teacher
        if len(self.teachers) == 0:
            raise ValueError("At least one teacher is required.")

        # Check for positive k
        if self.k <= 0:
            raise ValueError("k must be a positive integer.")
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'TeacherSubjectSetCover':
        """
        Create a TeacherSubjectSetCover instance from a dictionary.

        Args:
            data (Dict): Dictionary containing problem instance data.

        Returns:
            TeacherSubjectSetCover: A new TeacherSubjectSetCover instance.
        """
        required_keys = {'teachers', 'subjects', 'k'}
        if not all(key in data for key in required_keys):
            raise ValueError(f"Missing required keys. Required: {required_keys}")
        
        teachers = {Teacher.from_dict(teacher_data) for teacher_data in data['teachers']}
        subjects = set(data['subjects'])
        k = data['k']

        return cls(
            teachers=teachers,
            subjects=subjects,
            k=k
        )