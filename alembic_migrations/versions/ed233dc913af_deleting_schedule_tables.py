"""deleting schedule tables

Revision ID: ed233dc913af
Revises: 12b7d26b01d7
Create Date: 2022-09-28 19:15:43.828895

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Sequence
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.ddl import DropSequence, CreateSequence

# revision identifiers, used by Alembic.
revision = 'ed233dc913af'
down_revision = '12b7d26b01d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'main_schedule_info',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('timetable_id', sa.Integer(), nullable=True),
        sa.Column('user_type_is_student', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], )
    )
    op.execute('INSERT INTO main_schedule_info '
               'SELECT teacher_user.user_id, teacher_spbu.tt_id, False FROM teacher_user, teacher_spbu '
               'WHERE teacher_user.teacher_spbu_id = teacher_spbu.teacher_spbu_id;')
    op.execute('INSERT INTO main_schedule_info '
               'SELECT student.user_id, "group".tt_id, True FROM student, "group" '
               'WHERE student.group_id = "group".group_id;')
    op.drop_table('teacher_study_event')
    op.drop_table('student_study_event')
    op.drop_table('subject')
    op.drop_table('teacher_user')
    op.drop_table('teacher_spbu')
    op.drop_table('student')
    op.drop_column('group', 'is_received_schedule')
    op.execute(DropSequence(Sequence("teacher_event_id_seq")))
    op.execute(DropSequence(Sequence("student_event_id_seq")))
    op.execute(DropSequence(Sequence("subject_id_seq")))
    op.execute(DropSequence(Sequence("teacher_user_id_seq")))
    op.execute(DropSequence(Sequence("teacher_spbu_id_seq")))
    op.execute(DropSequence(Sequence("student_id_seq")))


def downgrade() -> None:
    op.add_column('group', sa.Column('is_received_schedule', sa.BOOLEAN(), autoincrement=False, nullable=True))

    student_id_seq = Sequence("student_id_seq")
    op.execute(CreateSequence(student_id_seq))
    op.create_table(
        'student',
        sa.Column('student_id', sa.INTEGER(), server_default=student_id_seq.next_value(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.group_id'], name='student_group_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='student_user_id_fkey'),
        sa.PrimaryKeyConstraint('student_id', name='student_pkey')
    )

    teacher_spbu_id_seq = Sequence("teacher_spbu_id_seq")
    op.execute(CreateSequence(teacher_spbu_id_seq))
    op.create_table(
        'teacher_spbu',
        sa.Column('teacher_spbu_id', sa.INTEGER(), server_default=teacher_spbu_id_seq.next_value(), nullable=False),
        sa.Column('tt_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('full_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('teacher_spbu_id', name='teacher_spbu_pkey'),
        postgresql_ignore_search_path=False
    )

    teacher_user_id_seq = Sequence("teacher_user_id_seq")
    op.execute(CreateSequence(teacher_user_id_seq))
    op.create_table(
        'teacher_user',
        sa.Column('teacher_user_id', sa.INTEGER(), server_default=teacher_user_id_seq.next_value(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('teacher_spbu_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ['teacher_spbu_id'], ['teacher_spbu.teacher_spbu_id'], name='teacher_user_teacher_spbu_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='teacher_user_user_id_fkey'),
        sa.PrimaryKeyConstraint('teacher_user_id', name='teacher_user_pkey')
    )

    subject_id_seq = Sequence("subject_id_seq")
    op.execute(CreateSequence(subject_id_seq))
    op.create_table(
        'subject',
        sa.Column('subject_id', sa.INTEGER(), server_default=subject_id_seq.next_value(), nullable=False),
        sa.Column('subject_name', sa.VARCHAR(length=150), autoincrement=False, nullable=True),
        sa.Column('subject_format', sa.VARCHAR(length=150), autoincrement=False, nullable=True),
        sa.Column('locations', sa.VARCHAR(length=1000), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('subject_id', name='subject_pkey'),
        postgresql_ignore_search_path=False
    )

    student_event_id_seq = Sequence("student_event_id_seq")
    op.execute(CreateSequence(student_event_id_seq))
    op.create_table(
        'student_study_event',
        sa.Column('student_event_id', sa.INTEGER(), server_default=student_event_id_seq.next_value(), nullable=False),
        sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('date', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('start_time', postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column('end_time', postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column('subject_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('educator', sa.VARCHAR(length=300), autoincrement=False, nullable=True),
        sa.Column('is_canceled', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.group_id'], name='student_study_event_group_id_fkey'),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.subject_id'], name='student_study_event_subject_id_fkey'),
        sa.PrimaryKeyConstraint('student_event_id', name='student_study_event_pkey')
    )

    teacher_event_id_seq = Sequence("teacher_event_id_seq")
    op.execute(CreateSequence(teacher_event_id_seq))
    op.create_table(
        'teacher_study_event',
        sa.Column('teacher_event_id', sa.INTEGER(), server_default=teacher_event_id_seq.next_value(), nullable=False),
        sa.Column('teacher_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('date', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('start_time', postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column('end_time', postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column('subject_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('groups', sa.VARCHAR(length=300), autoincrement=False, nullable=True),
        sa.Column('is_canceled', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.subject_id'], name='teacher_study_event_subject_id_fkey'),
        sa.ForeignKeyConstraint(
            ['teacher_id'], ['teacher_spbu.teacher_spbu_id'], name='teacher_study_event_teacher_id_fkey'
        ),
        sa.PrimaryKeyConstraint('teacher_event_id', name='teacher_study_event_pkey')
    )
    op.drop_table('main_schedule_info')
