import React from "react";

export default function ScoreBadge({ score = 0, grade = "-" }) {
	return (
		<div className="score">
			<div className="score-bubble" aria-hidden>
				<div className="score-num">{score}</div>
				<div className="score-grade">{grade}</div>
			</div>
		</div>
	);
}
