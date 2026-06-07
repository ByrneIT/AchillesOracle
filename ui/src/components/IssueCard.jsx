import React from "react";

export default function IssueCard({ issue = {} }) {
	const {
		name = "Unnamed check",
		status = "pass",
		severity = "",
		details = "",
		recommendation = ""
	} = issue;

	const cls = `issue-card ${status === "warn" ? "warn" : status === "error" ? "error" : "pass"}`;

	return (
		<div className={cls}>
			<div className="title-row">
				<h3>{name}</h3>
				<div className="small-muted">{severity}</div>
			</div>
			<p>{details}</p>
			{recommendation && (
				<p className="small-muted">
					<strong>Fix:</strong> {recommendation}
				</p>
			)}
		</div>
	);
}
