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
  manageMutationKeys,
  manageQueryKeys,
  updateSkillList,
} from "@/Api/calls/manage";
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
    queryKey: manageQueryKeys.skillLists,
    queryFn: loadManageDoctrines,
  });

  const deleteMutation = useMutation({
    mutationKey: manageMutationKeys.deleteSkillList,
    mutationFn: (pk: number) => deleteSkillList(pk),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: manageQueryKeys.skillLists });
    },
  });

  const updateMutation = useMutation({
    mutationKey: manageMutationKeys.updateSkillList,
    mutationFn: ({ pk, payload }: { pk: number; payload: SkillListUpdateRequest }) =>
      updateSkillList(pk, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData<ManageSkillListSchema[]>(
        manageQueryKeys.skillLists,
        (old) => old?.map((item) => (item.id === updated.id ? updated : item))
      );
    },
  });

  // Resolves to false on an error, the error itself is shown by the alert below
  const { mutateAsync: updateMutateAsync } = updateMutation;
  const handleUpdate = useCallback(
    (pk: number, payload: SkillListUpdateRequest) =>
      updateMutateAsync({ pk, payload }).then(
        () => true,
        () => false
      ),
    [updateMutateAsync]
  );

  const { mutate: deleteMutate } = deleteMutation;
  const handleDelete = useCallback(
    (doctrine: ManageSkillListSchema) => {
      if (
        window.confirm(
          t('Are you sure you want to delete doctrine "{{name}}"?', {
            name: doctrine.name,
          })
        )
      ) {
        deleteMutate(doctrine.id);
      }
    },
    [t, deleteMutate]
  );

  // Stable callbacks: new ones would rebuild the columns and reset an open inline edit
  const handleEdit = useCallback(
    (doctrine: ManageSkillListSchema) =>
      setModalState({ show: true, doctrineToEdit: doctrine }),
    []
  );
  const handleViewSkills = useCallback(
    (doctrineId: number) => setSkillsModalState({ show: true, doctrineId }),
    []
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
            onEdit={handleEdit}
            onDelete={handleDelete}
            onViewSkills={handleViewSkills}
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
