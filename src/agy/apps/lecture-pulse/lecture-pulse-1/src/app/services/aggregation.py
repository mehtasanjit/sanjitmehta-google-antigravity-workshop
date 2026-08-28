from sqlalchemy import func
from app.models import (
    Poll, PollOption, PollResponse, PollResponseOption,
    Question, QuestionUpvote, Pulse, PulseResponse,
)


def poll_results(db, poll: Poll) -> dict:
    total_respondents = db.query(func.count(PollResponse.id)).filter(
        PollResponse.poll_id == poll.id
    ).scalar() or 0

    rows = db.query(
        PollOption.id,
        PollOption.text,
        func.count(PollResponseOption.id)
    ).outerjoin(
        PollResponseOption, PollResponseOption.option_id == PollOption.id
    ).filter(
        PollOption.poll_id == poll.id
    ).group_by(
        PollOption.id,
        PollOption.text,
        PollOption.position
    ).order_by(
        PollOption.position
    ).all()

    options = [
        {"option_id": row[0], "text": row[1], "count": row[2]}
        for row in rows
    ]

    if poll.is_quiz:
        correct = db.query(
            func.count(func.distinct(PollResponseOption.response_id))
        ).join(
            PollOption, PollOption.id == PollResponseOption.option_id
        ).filter(
            PollOption.poll_id == poll.id,
            PollOption.is_correct == True
        ).scalar() or 0
        rate = round(correct / total_respondents, 3) if total_respondents else 0.0
    else:
        rate = None

    return {
        'poll_id': poll.id,
        'poll_type': poll.poll_type,
        'is_quiz': poll.is_quiz,
        'total_respondents': total_respondents,
        'options': options,
        'correct_answer_rate': rate
    }


def question_ranking(db, session_id) -> list[dict]:
    results = db.query(
        Question,
        func.count(QuestionUpvote.id).label('upvotes')
    ).outerjoin(
        QuestionUpvote, QuestionUpvote.question_id == Question.id
    ).filter(
        Question.session_id == session_id
    ).group_by(
        Question.id
    ).order_by(
        func.count(QuestionUpvote.id).desc(),
        Question.created_at.asc()
    ).all()

    return [
        {
            'id': q.id,
            'session_id': q.session_id,
            'author_subject': q.author_subject,
            'text': q.text,
            'status': q.status,
            'created_at': q.created_at,
            'upvotes': upvotes
        }
        for q, upvotes in results
    ]


def pulse_sentiment(db, pulse: Pulse) -> dict:
    rows = db.query(
        PulseResponse.rating,
        func.count(PulseResponse.id)
    ).filter(
        PulseResponse.pulse_id == pulse.id
    ).group_by(
        PulseResponse.rating
    ).all()

    distribution = {str(i): 0 for i in range(1, 6)}
    total = 0
    weighted = 0
    for rating, count in rows:
        if rating is not None and str(rating) in distribution:
            distribution[str(rating)] = count
            total += count
            weighted += rating * count

    average = round(weighted / total, 3) if total else None

    return {
        'pulse_id': pulse.id,
        'total': total,
        'average': average,
        'distribution': distribution
    }
