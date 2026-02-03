const rankStudents = (students) => {
    // Sort students by total marks in descending order
    students.sort((a, b) => b.totalMarks - a.totalMarks);

    // Assign ranks based on sorted order
    let currentRank = 1;
    for (let i = 0; i < students.length; i++) {
        if (i > 0 && students[i].totalMarks < students[i - 1].totalMarks) {
            currentRank = i + 1; // Update rank only if total marks change
        }
        students[i].rank = currentRank;
    }

    return students;
};

const calculatePercentage = (totalMarks, maxMarks) => {
    return ((totalMarks / maxMarks) * 100).toFixed(2);
};

const prepareRankingData = (studentRecords, maxMarks) => {
    return studentRecords.map(student => {
        const totalMarks = student.subjects.reduce((sum, subject) => sum + subject.marks, 0);
        const percentage = calculatePercentage(totalMarks, maxMarks);
        
        return {
            enrollmentNumber: student.enrollmentNumber,
            name: student.name,
            totalMarks: totalMarks,
            percentage: percentage,
        };
    });
};

export { rankStudents, prepareRankingData };