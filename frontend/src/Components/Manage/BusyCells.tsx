// React
import React from "react";

// Third Party
import { useIsMutating } from "@tanstack/react-query";
import { Button } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import {
  InlineEditCell,
  type InlineEditCellProps,
} from "@/Components/Manage/InlineEditCell";

type MutationKey = readonly string[];

// The cells read the state of a mutation themselves: as an argument of the
// columns it would rebuild them on every save and reset an open inline edit.
const useIsBusy = (mutationKey: MutationKey) =>
  useIsMutating({ mutationKey }) > 0;

/** Inline edit cell that cannot be opened while the mutation runs. */
export const BusyInlineEditCell: React.FC<
  InlineEditCellProps & { mutationKey: MutationKey }
> = ({ mutationKey, ...props }) => (
  <InlineEditCell {...props} disabled={useIsBusy(mutationKey)} />
);

/** Button that is disabled while the mutation runs. */
export const BusyButton: React.FC<
  React.ComponentProps<typeof Button> & { mutationKey: MutationKey }
> = ({ mutationKey, ...props }) => (
  <Button {...props} disabled={useIsBusy(mutationKey)} />
);
