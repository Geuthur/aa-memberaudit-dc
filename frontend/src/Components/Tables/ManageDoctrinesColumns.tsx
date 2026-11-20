// Third Party
import { type BaseColumnDef, renderTooltip } from "aa-geuthur-react";
import type { TFunction } from "i18next";
import { BookOpen, Edit2, Eye, EyeOff, Trash2 } from "lucide-react";
import { Badge, Button, ButtonGroup } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import type { ManageSkillListSchema, SkillListUpdateRequest } from "@/Api/schema";
import { InlineEditCell } from "@/Components/Manage/InlineEditCell";

export const getManageDoctrinesColumns = (
  t: TFunction,
  isDeleting: boolean,
  isUpdating: boolean,
  onEdit: (doctrine: ManageSkillListSchema) => void,
  onDelete: (doctrine: ManageSkillListSchema) => void,
  onViewSkills: (doctrineId: number) => void,
  onUpdate: (doctrineId: number, payload: SkillListUpdateRequest) => void
): BaseColumnDef<ManageSkillListSchema>[] => [
  {
    id: "name",
    header: () => t("Doctrine Name"),
    accessorKey: "name",
    cell: ({ row }) => (
      <div className="d-flex align-items-center gap-2">
        <InlineEditCell
          value={row.original.name}
          label={t("Doctrine Name")}
          disabled={isUpdating}
          onSave={(name) => onUpdate(row.original.id, { name })}
        >
          <span className="fw-bold">{row.original.name}</span>
        </InlineEditCell>
        <Badge bg="secondary" pill title={t("Required Skills Count")}>
          {row.original.skill_count} {t("skills")}
        </Badge>
      </div>
    ),
  },
  {
    id: "category",
    header: () => t("Category"),
    accessorKey: "category",
    cell: ({ row }) => (
      <InlineEditCell
        value={row.original.category ?? ""}
        label={t("Category")}
        disabled={isUpdating}
        onSave={(category) => onUpdate(row.original.id, { category })}
      >
        <Badge bg="info">{row.original.category || t("Uncategorized")}</Badge>
      </InlineEditCell>
    ),
  },
  {
    id: "ordering",
    header: () => t("Order Weight"),
    accessorKey: "ordering",
    cell: ({ row }) => (
      <InlineEditCell
        value={String(row.original.ordering)}
        label={t("Order Weight")}
        type="number"
        disabled={isUpdating}
        onSave={(ordering) => {
          // Ignore empty or non-integer input instead of sending 0 or a fraction
          if (/^\d+$/.test(ordering.trim())) {
            onUpdate(row.original.id, { ordering: Number(ordering) });
          }
        }}
      >
        <span className="text-muted">{row.original.ordering}</span>
      </InlineEditCell>
    ),
  },
  {
    id: "active",
    header: () => t("Active"),
    accessorKey: "active",
    cell: ({ row }) =>
      renderTooltip(
        row.original.active ? t("Click to deactivate") : t("Click to activate"),
        <Button
          size="sm"
          variant={row.original.active ? "success" : "secondary"}
          className="d-inline-flex align-items-center gap-1"
          aria-label={row.original.active ? t("Deactivate") : t("Activate")}
          disabled={isUpdating}
          onClick={() =>
            onUpdate(row.original.id, { active: !row.original.active })
          }
        >
          {row.original.active ? <Eye size={12} /> : <EyeOff size={12} />}
          <span>{row.original.active ? t("Active") : t("Inactive")}</span>
        </Button>
      ),
  },
  {
    id: "actions",
    header: () => t("Actions"),
    cell: ({ row }) => (
      <ButtonGroup size="sm">
        {renderTooltip(
          t("View Skills"),
          <Button
            variant="info"
            aria-label={t("View Skills")}
            onClick={() => onViewSkills(row.original.id)}
          >
            <BookOpen size={14} />
          </Button>
        )}
        {renderTooltip(
          t("Edit Doctrine"),
          <Button
            variant="primary"
            aria-label={t("Edit Doctrine")}
            onClick={() => onEdit(row.original)}
          >
            <Edit2 size={14} />
          </Button>
        )}
        {renderTooltip(
          t("Delete Doctrine"),
          <Button
            variant="danger"
            aria-label={t("Delete Doctrine")}
            disabled={isDeleting}
            onClick={() => onDelete(row.original)}
          >
            <Trash2 size={14} />
          </Button>
        )}
      </ButtonGroup>
    ),
  },
];
