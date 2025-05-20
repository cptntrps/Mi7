# Project Manager Coordinator Test Prompt

## Topic for the Discussion
"Design and implement a company-wide cybersecurity training program for employees of all technical levels"

## Instructions for Testing

1. Create a new task force using the "Auto-Generate Task Force" feature with the above topic
2. Make sure to select "project_manager" as the coordinator archetype
3. Set the number of discussion rounds to 3 (to test progress tracking between rounds)
4. Run the discussion and observe the following key phases:

### Phase 1: Initial Project Plan
After starting the discussion, the Project Manager coordinator should create an initial project plan with:
- Clear project name and objectives
- Timeline with start/end dates and key milestones
- Required resources (skills, tools, constraints)
- Risk management section

### Phase 2: Progress Tracking
At the end of rounds 1 and 2 (but not 3), the Project Manager should generate:
- A progress report showing completion status
- Key points from the discussion
- Next steps with priorities and assignments
- Risks and mitigations

### Phase 3: Plan Adjustments
After each progress report, the Project Manager should propose adjustments:
- Modified objectives based on the discussion
- Timeline adjustments if needed
- Resource adjustments (skills, tools, constraints)
- Risk adjustments

### Phase 4: Final Output
At the end of the discussion, the Project Manager should:
- Provide a comprehensive summary
- Make a final assessment
- Generate an adaptive final output

## Success Criteria

The test is successful if:
1. All JSON objects are properly parsed without errors
2. Each phase produces structured, meaningful content
3. The plan adjustments are relevant to the progress reports
4. The final output incorporates information from all phases

## Potential Issues to Watch For

1. JSON parsing errors in the console
2. Missing required keys in any of the structured outputs
3. Disconnection between progress reports and plan adjustments
4. Poor integration of the project management elements into the final output 