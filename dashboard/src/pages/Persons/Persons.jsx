import { useState, useEffect } from "react";
import { Search, UserPlus, Users, UserCheck, Clock } from "lucide-react";

import PageTitle from "../../components/ui/PageTitle";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import StatCard from "../../components/ui/StatCard";
import PersonCard from "../../components/persons/PersonCard";
import UploadModal from "../../components/dataset/UploadModal";
import { PersonService } from "../../services/personService";

function timeAgo(dateStr) {
  if (!dateStr) return "Belum pernah";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function Persons() {
  const [query, setQuery] = useState("");
  const [persons, setPersons] = useState(null);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const loadData = () => {
    PersonService.getPersons()
      .then((data) => setPersons(data.persons))
      .catch((err) => setError(err.message));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (error) return <p className="text-red-400">Gagal memuat: {error}</p>;
  if (!persons) return <p className="text-slate-500">Memuat data...</p>;

  const filtered = persons.filter((p) =>
    p.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <PageTitle title="Persons" subtitle="Kelola daftar orang yang dikenali sistem" />
        <Button icon={UserPlus} onClick={() => setModalOpen(true)}>
          Add Person
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <StatCard title="Total Persons" value={persons.length} icon={<Users size={20} />} accent="blue" />
        <StatCard
          title="Registered"
          value={persons.filter((p) => p.status === "registered").length}
          icon={<UserCheck size={20} />}
          accent="emerald"
        />
        <StatCard
          title="Pending"
          value={persons.filter((p) => p.status === "pending").length}
          icon={<Clock size={20} />}
          accent="amber"
        />
      </div>

      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <Input
          placeholder="Cari nama..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ paddingLeft: "2.5rem" }}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
        {filtered.map((p) => (
          <PersonCard
            key={p.name}
            name={p.name}
            role="Person"
            status={p.status}
            images={p.images}
            lastSeen={timeAgo(p.last_seen)}
          />
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-center text-slate-500 py-10">Tidak ada hasil untuk "{query}"</p>
      )}

      <UploadModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onUploaded={loadData}
      />
    </div>
  );
}