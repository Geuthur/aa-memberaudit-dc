// AA Memberaudit Doctrine Checker
import type { CharacterSchema } from "@/Api/schema";

export interface DoctrineStatus {
  id?: number;
  name: string;
  category: string;
  order: number;
  character_id?: number | null;
  skills: Array<{ skill_name: string; required_level: number }>;
}

export interface MemberDoctrineRow {
  character: CharacterSchema;
  alts?: CharacterSchema[] | null;
  doctrines: Record<string, DoctrineStatus>;
  isAudited: boolean;
}
