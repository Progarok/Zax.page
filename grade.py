def calculate_grade(score):
    """Return the grade for a numeric score."""
    try:
        score = float(score)
    except ValueError:
        return None

    if score < 0 or score > 100:
        return None

    if score >= 80:
        return 'A'
    if score >= 70:
        return 'B'
    if score >= 60:
        return 'C'
    if score >= 50:
        return 'D'
    return 'F'


def main():
    print('โปรแกรมคิดเกรด')
    print('กรุณากรอกคะแนนระหว่าง 0-100')

    score_input = input('คะแนน: ').strip()
    grade = calculate_grade(score_input)

    if grade is None:
        print('ค่าที่กรอกไม่ถูกต้อง กรุณากรอกตัวเลข 0-100')
    else:
        print(f'เกรดของคุณคือ: {grade}')


if __name__ == '__main__':
    main()
