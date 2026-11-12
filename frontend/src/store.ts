import { create } from "zustand";
import type { Chapter, Page, Region } from "./types";

type StudioState = {
  chapter: Chapter | null;
  selectedPageId: number | null;
  selectedRegionId: number | null;
  setChapter: (chapter: Chapter) => void;
  selectPage: (pageId: number) => void;
  selectRegion: (regionId: number | null) => void;
  updateRegion: (region: Region) => void;
};

export const useStudioStore = create<StudioState>((set) => ({
  chapter: null,
  selectedPageId: null,
  selectedRegionId: null,
  setChapter: (chapter) =>
    set({
      chapter,
      selectedPageId: chapter.pages[0]?.id ?? null,
    }),
  selectPage: (selectedPageId) => set({ selectedPageId, selectedRegionId: null }),
  selectRegion: (selectedRegionId) => set({ selectedRegionId }),
  updateRegion: (updated) =>
    set((state) => ({
      chapter: state.chapter
        ? {
            ...state.chapter,
            pages: state.chapter.pages.map((page) => ({
              ...page,
              regions: page.regions.map((region) =>
                region.id === updated.id ? updated : region,
              ),
            })),
          }
        : null,
    })),
}));
