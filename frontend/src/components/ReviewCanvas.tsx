import { useEffect, useState } from "react";
import { Image as KonvaImage, Layer, Rect, Stage, Text } from "react-konva";
import useImage from "use-image";
import type { Region } from "../types";

type Props = {
  imageUrl: string;
  regions: Region[];
  selectedRegionId: number | null;
  onSelect: (id: number) => void;
  onMove: (region: Region, bbox: [number, number, number, number]) => void;
};

export function ReviewCanvas({ imageUrl, regions, selectedRegionId, onSelect, onMove }: Props) {
  const [image] = useImage(imageUrl);
  const [scale, setScale] = useState(1);
  const imageWidth = image?.width ?? 1200;
  const imageHeight = image?.height ?? 1600;
  const stageWidth = Math.min(850, window.innerWidth - 420);
  const nextScale = stageWidth / imageWidth;
  useEffect(() => setScale(nextScale), [nextScale]);
  return (
    <div className="canvas-shell">
      <Stage width={imageWidth * scale} height={imageHeight * scale} scaleX={scale} scaleY={scale}>
        <Layer>
          {image && <KonvaImage image={image} width={imageWidth} height={imageHeight} />}
          {regions.map((region) => {
            const [x1, y1, x2, y2] = region.bbox;
            const selected = region.id === selectedRegionId;
            return (
              <Rect
                key={region.id}
                x={x1}
                y={y1}
                width={x2 - x1}
                height={y2 - y1}
                stroke={selected ? "#ffd166" : "#6ee7b7"}
                strokeWidth={selected ? 5 : 3}
                draggable
                onClick={() => onSelect(region.id)}
                onDragEnd={(event) => {
                  const node = event.target;
                  const dx = node.x() - x1;
                  const dy = node.y() - y1;
                  node.position({ x: x1, y: y1 });
                  onMove(region, [x1 + dx, y1 + dy, x2 + dx, y2 + dy]);
                }}
              />
            );
          })}
          {regions.map((region) => {
            const [x1, y1, x2, y2] = region.bbox;
            return (
              <Text
                key={`text-${region.id}`}
                x={x1 + 8}
                y={y1 + 8}
                width={x2 - x1 - 16}
                text={region.translated_text || region.original_text}
                fontSize={region.font_size ?? 28}
                fill="#111827"
                align="center"
                listening={false}
              />
            );
          })}
        </Layer>
      </Stage>
    </div>
  );
}
