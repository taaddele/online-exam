from django.contrib import admin
from .models import *
from django.utils.html import format_html

class StudentAnswerAdmin(admin.ModelAdmin):
    # This will display columns like student name, question, and selected answer in the list view
    list_display = ('student', 'question', 'selected_answer', 'correct_answer', 'question_number')

    # This will allow sorting by 'student' and 'question' (optional)
    list_filter = ('student', 'question')
    def has_add_permission(self, request):
        """Disallow adding new StudentAnswer entries from the admin interface."""
        return False
    def question_number(self, obj):
        return f"Question {obj.question.id}"  # Display the question number as 'Question X'
    question_number.short_description = 'Question Number'

    def correct_answer(self, obj):
        return obj.question.get_answer_text()  # Displays the correct answer for the question
    correct_answer.short_description = 'Correct Answer'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # We add custom context to the change view (Student's answers page)
        obj = self.get_object(request, object_id)
        student = obj.student
        # Add the first_name and id_no to the context
        extra_context = extra_context or {}
        extra_context['student_details'] = {
            'first_name': student.first_name,
            'id_no': student.id_no
        }

        # Return the default change view with our extra context
        return super().change_view(request, object_id, form_url, extra_context)

    def get_student_answers(self, student):
        # Retrieve answers by the student for this exam
        return StudentAnswer.objects.filter(student=student)

    def student_answers_table(self, student):
        answers = self.get_student_answers(student)
        table_rows = ""
        for answer in answers:
            table_rows += f"<tr><td>{answer.question.id}</td><td>{answer.question.question}</td><td>{answer.selected_answer}</td><td>{answer.question.answer}</td></tr>"
        return format_html(f"""
        <table class="table">
            <thead>
                <tr>
                    <th>Question Number</th>
                    <th>Question</th>
                    <th>Your Answer</th>
                    <th>Correct Answer</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """)

    # For the admin `change_view`, override it to display the table as well as student details.
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Adding extra context for displaying student info and answers
        obj = self.get_object(request, object_id)
        student = obj.student
        extra_context = extra_context or {}
        extra_context['student_details'] = {
            'first_name': student.first_name,
            'id_no': student.id_no
        }
        extra_context['student_answers_table'] = self.student_answers_table(student)

        # Now pass the extra context into the base change_view function
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(ExamAttempt)
admin.site.register(StudentAnswer, StudentAnswerAdmin)
