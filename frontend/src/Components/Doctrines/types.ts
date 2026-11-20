export interface DoctrineItem {
  id?: number;
  name: string;
  category: string;
  order: number;
  skills: Array<{ skill_name: string; required_level: number }>;
}
