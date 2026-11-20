// React
import React, { useCallback, useState } from "react";

// Third Party
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Alert, Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import {
  deleteSkillList,
  loadManageDoctrines,
  updateSkillList,
} from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import type { ManageSkillListSchema, SkillListUpdateRequest } from "@/Api/schema";
import { ManageDoctrinesTable, ManageHeader } from "@/Components/Manage";
import DoctrineSkillsModal from "@/Components/Modals/DoctrineSkillsModal";
import ManageDoctrineModal from "@/Components/Modals/ManageDoctrineModal";

export const ManagePage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [modalState, setModalState] = useState<{
    show: boolean;
    doctrineToEdit: ManageSkillListSchema | null;
  }>({
    show: false,
    doctrineToEdit: null,
  });

  const [skillsModalState, setSkillsModalState] = useState<{
    show: boolean;
    doctrineId: number | null;
  }>({
    show: false,
    doctrineId: null,
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.ManageDoctrines,
    queryFn: loadManageDoctrines,
  });

  const deleteMutation = useMutation({
    mutationFn: (pk: number) => deleteSkillList(pk),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.ManageDoctrines });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ pk, payload }: { pk: number; payload: SkillListUpdateRequest }) =>
      updateSkillList(pk, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData<ManageSkillListSchema[]>(
        queryKeys.ManageDoctrines,
        (old) => old?.map((item) => (item.id === updated.id ? updated : item))
      );
    },
  });

  const { mutate: updateMutate } = updateMutation;
  const handleUpdate = useCallback(
    (pk: number, payload: SkillListUpdateRequest) => {
      updateMutate({ pk, payload });
    },
    [updateMutate]
  );

  const handleDelete = useCallback(
    (doctrine: ManageSkillListSchema) => {
      if (
        window.confirm(
          t('Are you sure you want to delete doctrine "{{name}}"?', {
            name: doctrine.name,
          })
        )
      ) {
        deleteMutation.mutate(doctrine.id);
      }
    },
    [t, deleteMutation]
  );

  return (
    <main>
      <ManageHeader
        onAddDoctrine={() =>
          setModalState({ show: true, doctrineToEdit: null })
        }
      />

      {updateMutation.isError && (
        <Alert variant="danger" dismissible onClose={() => updateMutation.reset()}>
          {updateMutation.error instanceof Error
            ? updateMutation.error.message
            : t("Failed to update skill list")}
        </Alert>
      )}
      {deleteMutation.isError && (
        <Alert variant="danger" dismissible onClose={() => deleteMutation.reset()}>
          {deleteMutation.error instanceof Error
            ? deleteMutation.error.message
            : t("Failed to delete skill list")}
        </Alert>
      )}

      <Card className="border-0 shadow-sm aa-panel">
        <Card.Body className="p-3">
          <ManageDoctrinesTable
            data={data || []}
            isLoading={isLoading}
            isError={isError}
            isDeleting={deleteMutation.isPending}
            isUpdating={updateMutation.isPending}
            onEdit={(doc) =>
              setModalState({ show: true, doctrineToEdit: doc })
            }
            onDelete={handleDelete}
            onViewSkills={(id) =>
              setSkillsModalState({ show: true, doctrineId: id })
            }
            onUpdate={handleUpdate}
          />
        </Card.Body>
      </Card>

      {/* Modals */}
      <ManageDoctrineModal
        show={modalState.show}
        doctrineToEdit={modalState.doctrineToEdit}
        onHide={() =>
          setModalState({ show: false, doctrineToEdit: null })
        }
      />

      <DoctrineSkillsModal
        show={skillsModalState.show}
        doctrineId={skillsModalState.doctrineId}
        onHide={() =>
          setSkillsModalState({ show: false, doctrineId: null })
        }
      />
    </main>
  );
};

export default ManagePage;
