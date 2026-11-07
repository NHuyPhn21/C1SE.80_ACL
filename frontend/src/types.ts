export type Region = {
  id: number;
  bbox: [number, number, number, number];
  original_text: string;
  translated_text: string;
  font_family: string | null;
  font_size: number | null;
  alignment: string | null;
};

export type Page = {
  id: number;
  page_number: number;
  status: string;
  original_url: string;
  clean_url: string | null;
  rendered_url: string | null;
  regions: Region[];
};

export type Chapter = {
  id: number;
  project_id: number;
  chapter_number: number;
  chapter_name: string | null;
  pages: Page[];
};
