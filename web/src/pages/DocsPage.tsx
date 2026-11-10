import { useLayoutEffect } from "react";
import { ExternalLink } from "lucide-react";
import { useI18n } from "@/i18n";
import { usePageHeader } from "@/contexts/usePageHeader";
import { cn } from "@/lib/utils";
import { PluginSlot } from "@/plugins";

/**
 * Kitsune Agent documentation.
 *
 * Upstream embedded Nous Research's hosted Hermes docs here. Kitsune's own docs are built from
 * `website/` and will be published as a GitHub Pages site; until that site is live this page links to
 * the docs source in the repository (GitHub refuses to be framed, so there is no iframe).
 * When the Pages site is live, point KITSUNE_DOCS_URL at it and render it in an iframe again.
 */
export const KITSUNE_DOCS_URL =
  "https://github.com/KingBeam5/kitsune-agent/tree/kitsune/website/docs";
export const KITSUNE_REPO_URL = "https://github.com/KingBeam5/kitsune-agent";

const DS_BUTTON_OUTLINED_LINK_CN = cn(
  "group relative inline-grid grid-cols-[auto_1fr_auto] items-center",
  "px-[.9em_.75em] py-[1.25em] gap-2",
  "leading-0 font-bold tracking-[0.2em] uppercase",
  "text-midground bg-transparent shadow-midground",
  "shadow-[inset_-1px_-1px_0_0_#00000080,inset_1px_1px_0_0_#ffffff80]",
);

export default function DocsPage() {
  const { t } = useI18n();
  const { setEnd } = usePageHeader();

  useLayoutEffect(() => {
    setEnd(
      <a
        href={KITSUNE_DOCS_URL}
        target="_blank"
        rel="noopener noreferrer"
        className={DS_BUTTON_OUTLINED_LINK_CN}
      >
        <ExternalLink className="size-3.5" />
        {t.app.openDocumentation}
      </a>,
    );
    return () => {
      setEnd(null);
    };
  }, [setEnd, t]);

  return (
    <div
      className={cn(
        "flex min-h-0 w-full min-w-0 flex-1 flex-col gap-4",
        "pt-1 sm:pt-2",
      )}
    >
      <PluginSlot name="docs:top" />
      <div
        className={cn(
          "max-w-2xl space-y-4 p-6",
          "rounded-sm border border-current/20",
        )}
      >
        <h2 className="text-lg font-bold tracking-wide text-midground">
          Kitsune Agent documentation
        </h2>
        <p className="text-text-secondary">
          The Kitsune Agent docs are written in the repository and are being
          corrected page by page. A hosted docs site is not live yet, so the
          pages open on GitHub.
        </p>
        <p className="text-text-secondary">
          Start with <strong>Getting Started → Installation</strong> and{" "}
          <strong>Official Sources &amp; Safety</strong>. Some pages are
          inherited from upstream Hermes Agent and may describe features or
          install methods that Kitsune Agent does not ship.
        </p>
        <p className="text-sm text-text-secondary">
          Source:{" "}
          <a
            className="underline"
            href={KITSUNE_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            github.com/KingBeam5/kitsune-agent
          </a>
        </p>
      </div>
      <PluginSlot name="docs:bottom" />
    </div>
  );
}
