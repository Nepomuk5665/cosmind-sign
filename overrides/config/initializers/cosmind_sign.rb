# frozen_string_literal: true

# Cosmind Sign (README.md, ADR-322): Cosmind's name, not DocuSeal's, in what DocuSeal writes into
# a signed document. The only Ruby we add: three overrides, applied once the app has loaded.
#
# - The signature's reason: DocuSeal's "Signed with DocuSeal.com" (the constant SIGN_REASON of
#   Submissions::GenerateResultAttachments, and Submissions::GenerateAuditTrail.sign_reason).
# - The audit trail's header: DocuSeal's add_logo draws its logo and the name "DocuSeal" linked to
#   docuseal.com; ours draws the same logo file (lib/pdf_icons/logo.png, which we replace with the
#   Cosmind mark) and "Cosmind Sign", without a link.
# - The PDF's creator: DocuSeal sets "DocuSeal (https://www.docuseal.com)" in three places just
#   before it writes a PDF; HexaPDF::Document#write puts "Cosmind Sign" in its place, and leaves any
#   other creator as it is.
#
# deploy/sign/docuseal/check.py fails when DocuSeal changes a file these rely on, so an upgrade
# looks at them again.
module CosmindSign
  NAME = 'Cosmind Sign'
  SIGN_REASON = 'Signed with Cosmind Sign'

  module_function

  def docuseal_creator
    "#{Docuseal.product_name} (#{Docuseal::PRODUCT_URL})"
  end

  module AuditTrail
    def sign_reason
      SIGN_REASON
    end

    def add_logo(column, _submission = nil)
      column.image(PdfIcons.logo_io, width: 40, height: 40, position: :float)

      column.formatted_text([{ text: NAME }],
                            font_size: 20,
                            font: [Submissions::GenerateAuditTrail::FONT_NAME, { variant: :bold }],
                            width: 200,
                            padding: [5, 0, 0, 8],
                            position: :float, text_align: :left)
    end
  end

  module PdfCreator
    def write(*args, **kwargs, &)
      info = trailer[:Info]
      info[:Creator] = NAME if info && info[:Creator] == CosmindSign.docuseal_creator

      super
    end
  end
end

Rails.application.config.after_initialize do
  Submissions::GenerateResultAttachments.send(:remove_const, :SIGN_REASON)
  Submissions::GenerateResultAttachments.const_set(:SIGN_REASON, CosmindSign::SIGN_REASON)
  Submissions::GenerateAuditTrail.singleton_class.prepend(CosmindSign::AuditTrail)
  HexaPDF::Document.prepend(CosmindSign::PdfCreator)
end
