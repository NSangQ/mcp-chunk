#ifndef STUDENT_H
#define STUDENT_H

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <algorithm>

// 학생 클래스 정의
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
};

// 학생 관리 시스템 클래스
class StudentManagementSystem {
private:
    std::vector<std::shared_ptr<Student>> students;

public:
    void addStudent(const std::string& name, int id);
    void addGrade(int studentId, float grade);
    void displayStudentInfo(int studentId) const;
    void displayAllStudents() const;
};

#endif // STUDENT_H 