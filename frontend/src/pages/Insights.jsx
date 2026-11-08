import Briefing from "../components/Briefing";
import WeekDigest from "../components/WeekDigest";
import AssigneeSuggester from "../components/AssigneeSuggester";
import Allocation from "../components/Allocation";
import DecisionMemory from "../components/DecisionMemory";
import HealthStory from "../components/HealthStory";
import Reminders from "../components/Reminders";
import Achievements from "../components/Achievements";
import Timeline from "../components/Timeline";
import RiskHeatmap from "../components/RiskHeatmap";
import PageHeader from "../components/PageHeader";

export default function Insights() {
  return (
    <div>
      <PageHeader variant="insights" kicker="Intelligence" title="Insights" subtitle="Briefings, suggestions and patterns from your data." />
      <Briefing />
      <div className="card">
        <h3>This week</h3>
        <WeekDigest />
      </div>
      <div className="card">
        <h3>Who should take this task?</h3>
        <AssigneeSuggester />
      </div>
      <div className="card">
        <h3>Resource allocation suggestions</h3>
        <Allocation />
      </div>
      <div className="card">
        <h3>Smart reminders</h3>
        <Reminders />
      </div>
      <div className="card">
        <h3>Project health story</h3>
        <HealthStory />
      </div>
      <div className="card">
        <h3>Decision memory</h3>
        <DecisionMemory />
      </div>
      <div className="card">
        <h3>Team achievements</h3>
        <Achievements />
      </div>
      <div className="card">
        <h3>Project timeline</h3>
        <Timeline />
      </div>
      <div className="card">
        <h3>Risk heatmap</h3>
        <RiskHeatmap />
      </div>
    </div>
  );
}
