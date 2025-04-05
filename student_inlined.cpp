#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <algorithm>

class Student {
private:
    std::string name;
    int studentId;
    std::vector<float> grades;

public:
    Student(const std::string& name, int id);
    void addGrade(float grade);
    float getAverage() const;
    std::string getName() const;
    int getId() const;
}

class StudentManagementSystem {
private:
    std::vector<std::shared_ptr<Student>> students;

public:
    void addStudent(const std::string& name, int id);
    void addGrade(int studentId, float grade);
    void displayStudentInfo(int studentId) const;
    void displayAllStudents() const;
}


Student::Student(const std::string& name, int id) : name(name), studentId(id) {}

void Student::addGrade(float grade) {
    grades.push_back(grade);
}

float Student::getAverage() const {
    if (grades.empty()) return 0.0f;
    float sum = 0.0f;
    for (float grade : grades) {
        sum += grade;
    }
    return sum / grades.size();
}

std::string Student::getName() const { return name; }
int Student::getId() const { return studentId; }

void StudentManagementSystem::addStudent(const std::string& name, int id) {
    students.push_back(std::make_shared<Student>(name, id));
}

void StudentManagementSystem::addGrade(int studentId, float grade) {
    auto it = std::find_if(students.begin(), students.end(),
        [studentId](const auto& student) {
            return student->getId() == studentId;
        });

    if (it != students.end()) {
        (*it)->addGrade(grade);
    }
}

void StudentManagementSystem::displayStudentInfo(int studentId) const {
    auto it = std::find_if(students.begin(), students.end(),
        [studentId](const auto& student) {
            return student->getId() == studentId;
        });

    if (it != students.end()) {
        std::cout << "학생 정보:\n";
        std::cout << "이름: " << (*it)->getName() << "\n";
        std::cout << "학번: " << (*it)->getId() << "\n";
        std::cout << "평균 성적: " << (*it)->getAverage() << "\n";
    } else {
        std::cout << "학생을 찾을 수 없습니다.\n";
    }
}

void StudentManagementSystem::displayAllStudents() const {
    std::cout << "\n전체 학생 목록:\n";
    for (const auto& student : students) {
        std::cout << "이름: " << student->getName() 
                  << ", 학번: " << student->getId() 
                  << ", 평균: " << student->getAverage() << "\n";
    }
}

int main() {
    StudentManagementSystem system;

    // 학생 추가
    system.addStudent("김철수", 2024001);
    system.addStudent("이영희", 2024002);
    system.addStudent("박민수", 2024003);

    // 성적 입력
    system.addGrade(2024001, 85.5f);
    system.addGrade(2024001, 90.0f);
    system.addGrade(2024002, 92.5f);
    system.addGrade(2024002, 88.0f);
    system.addGrade(2024003, 78.5f);
    system.addGrade(2024003, 95.0f);

    // 학생 정보 출력
    std::cout << "=== 학생 관리 시스템 ===\n";
    system.displayAllStudents();

    // 특정 학생 정보 조회
    std::cout << "\n특정 학생 정보 조회:\n";
    system.displayStudentInfo(2024002);

    return 0;
} 