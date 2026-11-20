// React
import React, { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { useUserData } from "aa-geuthur-react";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import { loadDoctrines } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import type { CharacterDoctrines, UserData } from "@/Api/schema";
import {
  CharacterBanner,
  CharacterSelector,
  DoctrineCategorySection,
  type DoctrineItem,
} from "@/Components/Doctrines";
import DoctrineSkillsModal from "@/Components/Modals/DoctrineSkillsModal";
import MissingSkillsModal from "@/Components/Modals/MissingSkillsModal";

export const DoctrinesPage: React.FC = () => {
  const { t } = useTranslation();
  const { characterId: paramCharId } = useParams<{ characterId?: string }>();

  // Modals state
  const [missingSkillsModal, setMissingSkillsModal] = useState<{
    show: boolean;
    characterId: number | null;
    doctrineId: number | null;
  }>({
    show: false,
    characterId: null,
    doctrineId: null,
  });

  const [doctrineSkillsModal, setDoctrineSkillsModal] = useState<{
    show: boolean;
    doctrineId: number | null;
    characterId: number | null;
  }>({
    show: false,
    doctrineId: null,
    characterId: null,
  });

  // Current user data
  const { data: userData } = useUserData<UserData>();

  const activeCharId = useMemo(() => {
    if (paramCharId) {
      return parseInt(paramCharId, 10);
    }
    return userData?.user.character_id ?? 0;
  }, [paramCharId, userData]);

  const [selectedCharId, setSelectedCharId] = useState<number | null>(null);

  const effectiveCharId = selectedCharId || activeCharId;

  // Doctrines query for the active/selected character
  const {
    data: doctrinesData,
    isLoading,
    isFetching,
    isError,
    error,
  } = useQuery({
    queryKey: effectiveCharId ? queryKeys.Doctrines(effectiveCharId) : ["Doctrines", 0],
    queryFn: () => loadDoctrines(effectiveCharId),
    enabled: Boolean(effectiveCharId),
  });

  const [characterMap, setCharacterMap] = useState<Record<number, CharacterDoctrines>>({});
  const [prevDoctrinesData, setPrevDoctrinesData] = useState<CharacterDoctrines[] | undefined>(undefined);

  if (doctrinesData !== prevDoctrinesData) {
    setPrevDoctrinesData(doctrinesData);
    if (doctrinesData && doctrinesData.length > 0) {
      const nextMap = { ...characterMap };
      for (const char of doctrinesData) {
        const existing = nextMap[char.character.character_id];
        if (!existing || Object.keys(char.doctrines).length > 0) {
          nextMap[char.character.character_id] = char;
        }
      }
      setCharacterMap(nextMap);
    }
  }

  const characterList = useMemo(() => {
    return Object.values(characterMap);
  }, [characterMap]);

  // Current character data to display
  const currentCharData: CharacterDoctrines | undefined = useMemo(() => {
    if (characterMap[effectiveCharId]) {
      return characterMap[effectiveCharId];
    }
    return (
      doctrinesData?.find((c) => c.character.character_id === effectiveCharId) ??
      doctrinesData?.[0]
    );
  }, [characterMap, effectiveCharId, doctrinesData]);

  // Group doctrines by category
  const categorizedDoctrines = useMemo(() => {
    if (!currentCharData?.doctrines) return {};

    const groups: Record<string, DoctrineItem[]> = {};

    Object.entries(currentCharData.doctrines).forEach(([docName, rawDoc]) => {
      const doc = rawDoc as DoctrineItem;
      const cat = doc.category?.trim() || t("Uncategorized");
      if (!groups[cat]) {
        groups[cat] = [];
      }
      groups[cat].push({
        ...doc,
        name: doc.name || docName,
      });
    });

    // Sort doctrines in each category by order
    Object.keys(groups).forEach((key) => {
      groups[key].sort((a, b) => a.order - b.order || a.name.localeCompare(b.name));
    });

    return groups;
  }, [currentCharData, t]);

  const handleOpenMissingSkills = (doctrineId: number) => {
    if (currentCharData) {
      setMissingSkillsModal({
        show: true,
        characterId: currentCharData.character.character_id,
        doctrineId,
      });
    }
  };

  const handleOpenDoctrineSkills = (doctrineId: number) => {
    setDoctrineSkillsModal({
      show: true,
      doctrineId,
      characterId: currentCharData?.character.character_id ?? null,
    });
  };

  const isCharacterSectionLoading =
    isFetching &&
    (!currentCharData || Object.keys(currentCharData.doctrines).length === 0);

  return (
    <main>
      {isLoading && (
        <div className="d-flex justify-content-center align-items-center py-5 gap-2">
          <span className="spinner-border spinner-border-sm" role="status" />
          <span>{t("Loading doctrines...")}</span>
        </div>
      )}

      {isError && (
        <div className="alert alert-danger mt-3" role="alert">
          {error instanceof Error ? error.message : t("Failed to load doctrines.")}
        </div>
      )}

      {characterList.length > 0 && (
        <div className="mt-3">
          <CharacterSelector
            characters={characterList}
            selectedCharId={currentCharData?.character.character_id ?? effectiveCharId}
            onSelectCharacter={setSelectedCharId}
          />

          {currentCharData && (
            <CharacterBanner character={currentCharData.character} />
          )}

          {isCharacterSectionLoading ? (
            <div className="d-flex justify-content-center align-items-center py-5 gap-2">
              <span className="spinner-border spinner-border-sm" role="status" />
              <span>{t("Loading doctrines for character...")}</span>
            </div>
          ) : Object.keys(categorizedDoctrines).length === 0 ? (
            <div className="alert alert-info" role="status">
              {t("No active doctrines found for this character.")}
            </div>
          ) : (
            Object.entries(categorizedDoctrines).map(([category, items]) => (
              <DoctrineCategorySection
                key={category}
                category={category}
                doctrines={items}
                onViewSkills={handleOpenDoctrineSkills}
                onViewMissingSkills={handleOpenMissingSkills}
              />
            ))
          )}
        </div>
      )}

      {/* Modals */}
      <MissingSkillsModal
        show={missingSkillsModal.show}
        characterId={missingSkillsModal.characterId}
        doctrineId={missingSkillsModal.doctrineId}
        onHide={() =>
          setMissingSkillsModal({ show: false, characterId: null, doctrineId: null })
        }
      />

      <DoctrineSkillsModal
        show={doctrineSkillsModal.show}
        doctrineId={doctrineSkillsModal.doctrineId}
        characterId={doctrineSkillsModal.characterId}
        onHide={() =>
          setDoctrineSkillsModal({ show: false, doctrineId: null, characterId: null })
        }
      />
    </main>
  );
};

export default DoctrinesPage;
