// React
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { useUserData } from "aa-geuthur-react";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import {
    auditCorporationMembers,
    loadCorporationMembers,
    } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import type { ActiveDoctrineOverview, UserData } from "@/Api/schema";
import {
    CorporationBadgesTable,
    CorporationFilterBar,
    CorporationHeader,
    CorporationMatrixTable,
    type DoctrineStatus,
    type MemberDoctrineRow,
} from "@/Components/Corporation";
import DoctrineSkillsModal from "@/Components/Modals/DoctrineSkillsModal";
import MissingSkillsModal from "@/Components/Modals/MissingSkillsModal";

export const CorporationDoctrinesPage: React.FC = () => {
    const { t } = useTranslation();
    const { corporationId: paramCorpId } = useParams<{ corporationId?: string }>();

    // Filter and display states
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
    const [viewMode, setViewMode] = useState<"badges" | "matrix">("badges");

    // Progressive audit state (keyed by `${corpId}_${characterId}`)
    const [auditedDoctrines, setAuditedDoctrines] = useState<
        Record<string, Record<string, DoctrineStatus>>
    >({});
    const [auditedKeys, setAuditedKeys] = useState<Set<string>>(new Set());
    const [isAuditing, setIsAuditing] = useState(false);

    const auditedKeysRef = useRef<Set<string>>(new Set());
    const auditingKeysRef = useRef<Set<string>>(new Set());

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

    const { data: userData } = useUserData<UserData>();

    const activeCorpId = useMemo(() => {
        if (paramCorpId) {
            return parseInt(paramCorpId, 10);
        }
        return userData?.user.corporation_id ?? 0;
    }, [paramCorpId, userData]);

    // Fast members & doctrine metadata fetch
    const {
        data: corpMembersData,
        isLoading: isMembersLoading,
        isError: isMembersError,
        error: membersError,
    } = useQuery({
        queryKey: activeCorpId
            ? queryKeys.CorporationMembers(activeCorpId)
            : ["CorporationMembers", 0],
        queryFn: () => loadCorporationMembers(activeCorpId),
        enabled: Boolean(activeCorpId),
    });

    // Background progressive batch audit
    useEffect(() => {
        if (
            !corpMembersData?.members ||
            corpMembersData.members.length === 0 ||
            !activeCorpId
        ) {
            return;
        }

        let isMounted = true;
        const corpId = activeCorpId;
        const allMembers = corpMembersData.members;
        const pendingMembers = allMembers.filter((m) => {
            const key = `${corpId}_${m.character.character_id}`;
            return !auditedKeysRef.current.has(key) && !auditingKeysRef.current.has(key);
        });

        if (pendingMembers.length === 0) {
            return;
        }

        const CHUNK_SIZE = 10;
        const pendingIds = pendingMembers.map((m) => m.character.character_id);
        const chunks: number[][] = [];
        for (let i = 0; i < pendingIds.length; i += CHUNK_SIZE) {
            chunks.push(pendingIds.slice(i, i + CHUNK_SIZE));
        }

        pendingIds.forEach((id) => auditingKeysRef.current.add(`${corpId}_${id}`));

        const runAudits = async () => {
            setIsAuditing(true);
            for (const chunk of chunks) {
                if (!isMounted) break;
                try {
                    const auditedResults = await auditCorporationMembers(corpId, chunk);
                    if (!isMounted) break;

                    setAuditedDoctrines((prev) => {
                        const next = { ...prev };
                        auditedResults.forEach((member) => {
                            next[`${corpId}_${member.character.character_id}`] = (member.doctrines ||
                                {}) as Record<string, DoctrineStatus>;
                        });
                        return next;
                    });

                    chunk.forEach((id) => {
                        const key = `${corpId}_${id}`;
                        auditedKeysRef.current.add(key);
                        auditingKeysRef.current.delete(key);
                    });

                    setAuditedKeys(new Set(auditedKeysRef.current));
                } catch (err) {
                    console.error("Failed to audit members chunk:", chunk, err);
                    if (isMounted) {
                        chunk.forEach((id) => {
                            const key = `${corpId}_${id}`;
                            auditedKeysRef.current.add(key);
                            auditingKeysRef.current.delete(key);
                        });
                        setAuditedKeys(new Set(auditedKeysRef.current));
                    }
                }
            }
            if (isMounted) {
                setIsAuditing(false);
            }
        };

        runAudits();

        return () => {
            isMounted = false;
        };
    }, [corpMembersData, activeCorpId]);

    // Extract all unique doctrine info and categories immediately from metadata
    const { allCategories, allDoctrineList } = useMemo(() => {
        if (!corpMembersData?.doctrines || corpMembersData.doctrines.length === 0) {
            return { allCategories: [], allDoctrineList: [] as ActiveDoctrineOverview[] };
        }
        const categories = new Set<string>();
        corpMembersData.doctrines.forEach((d) => {
            const cat = d.category?.trim() || t("Uncategorized");
            categories.add(cat);
        });

        const sortedDoctrines = [...corpMembersData.doctrines].sort(
            (a, b) => (a.order ?? 999) - (b.order ?? 999) || a.name.localeCompare(b.name)
        );

        return {
            allCategories: Array.from(categories).sort(),
            allDoctrineList: sortedDoctrines,
        };
    }, [corpMembersData, t]);

    // Filtered doctrines by selected category
    const activeDoctrines = useMemo(() => {
        if (selectedCategory === "ALL") {
            return allDoctrineList;
        }
        // Same label as in the category list: no category is "Uncategorized"
        return allDoctrineList.filter(
            (d) => (d.category?.trim() || t("Uncategorized")) === selectedCategory
        );
    }, [allDoctrineList, selectedCategory, t]);

    // Build member row data merging metadata with progressive audit results
    const memberRows = useMemo<MemberDoctrineRow[]>(() => {
        if (!corpMembersData?.members) return [];
        return corpMembersData.members.map((m) => {
            const charId = m.character.character_id;
            const key = `${activeCorpId}_${charId}`;
            return {
                character: m.character,
                alts: m.alts,
                doctrines: auditedDoctrines[key] || {},
                isAudited: auditedKeys.has(key),
            };
        });
    }, [corpMembersData, activeCorpId, auditedDoctrines, auditedKeys]);

    // Filtered members by search
    const filteredMembers = useMemo(() => {
        return memberRows.filter((member) => {
            // Search term filter
            if (searchTerm.trim()) {
                const lower = searchTerm.toLowerCase();
                const matchesMain = member.character.character_name
                    .toLowerCase()
                    .includes(lower);
                const matchesAlts =
                    member.alts &&
                    member.alts.some((alt) => alt.character_name.toLowerCase().includes(lower));
                if (!matchesMain && !matchesAlts) {
                    return false;
                }
            }

            return true;
        });
    }, [memberRows, searchTerm]);

    const handleOpenMissingSkills = (charId: number, doctrineId: number) => {
        setMissingSkillsModal({
            show: true,
            characterId: charId,
            doctrineId,
        });
    };

    const handleOpenDoctrineSkills = (doctrineId: number, characterId?: number | null) => {
        setDoctrineSkillsModal({
            show: true,
            doctrineId,
            characterId: characterId ?? null,
        });
    };

    const totalMembersCount = corpMembersData?.members.length ?? 0;
    const currentCorpAuditedCount = useMemo(() => {
        if (!corpMembersData?.members) return 0;
        return corpMembersData.members.filter((m) =>
            auditedKeys.has(`${activeCorpId}_${m.character.character_id}`)
        ).length;
    }, [corpMembersData, activeCorpId, auditedKeys]);

    const auditProgressPercent =
        totalMembersCount > 0
            ? Math.round((currentCorpAuditedCount / totalMembersCount) * 100)
            : 0;

    const displayedCorpName = useMemo(() => {
        if (corpMembersData?.corporation_name) {
            return corpMembersData.corporation_name;
        }
        if (corpMembersData?.members && corpMembersData.members.length > 0) {
            return corpMembersData.members[0].character.corporation_name;
        }
        if (!paramCorpId && userData?.user.corporation_name) {
            return userData.user.corporation_name;
        }
        return t("Corporation Doctrines");
    }, [corpMembersData, paramCorpId, userData, t]);

    return (
        <main>
            {isMembersLoading && (
                <div className="d-flex justify-content-center align-items-center py-5 gap-2">
                    <span className="spinner-border spinner-border-sm" role="status" />
                    <span>{t("Loading corporation members...")}</span>
                </div>
            )}

            {isMembersError && (
                <div className="alert alert-danger mt-3" role="alert">
                    {membersError instanceof Error
                        ? membersError.message
                        : t("Failed to load corporation doctrines.")}
                </div>
            )}

            {corpMembersData && (
                <div className="mt-3">
                    <CorporationHeader
                        corpId={activeCorpId}
                        corpName={displayedCorpName}
                        auditedCount={currentCorpAuditedCount}
                        totalMembersCount={totalMembersCount}
                        activeDoctrinesCount={allDoctrineList.length}
                        isAuditing={isAuditing}
                        auditProgressPercent={auditProgressPercent}
                        viewMode={viewMode}
                        onViewModeChange={setViewMode}
                    />

                    <CorporationFilterBar
                        searchTerm={searchTerm}
                        onSearchChange={setSearchTerm}
                        selectedCategory={selectedCategory}
                        onCategoryChange={setSelectedCategory}
                        categories={allCategories}
                    />

                    {filteredMembers.length === 0 ? (
                        <div className="alert alert-info">
                            {t("No members found matching your search or filter.")}
                        </div>
                    ) : viewMode === "badges" ? (
                        <CorporationBadgesTable
                            members={filteredMembers}
                            activeDoctrines={activeDoctrines}
                            onOpenSkills={handleOpenDoctrineSkills}
                            onOpenMissingSkills={handleOpenMissingSkills}
                        />
                    ) : (
                        <CorporationMatrixTable
                            members={filteredMembers}
                            activeDoctrines={activeDoctrines}
                            onOpenSkills={handleOpenDoctrineSkills}
                            onOpenMissingSkills={handleOpenMissingSkills}
                        />
                    )}
                </div>
            )}

            {/* Modals */}
            <MissingSkillsModal
                show={missingSkillsModal.show}
                characterId={missingSkillsModal.characterId}
                doctrineId={missingSkillsModal.doctrineId}
                onHide={() =>
                    setMissingSkillsModal({
                        show: false,
                        characterId: null,
                        doctrineId: null,
                    })
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

export default CorporationDoctrinesPage;
